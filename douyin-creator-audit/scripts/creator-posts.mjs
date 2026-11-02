#!/usr/bin/env node
/**
 * creator-posts.mjs —— 抖音博主作品盘点
 * 输入：主页链接 / v.douyin.com 短链 / sec_uid / 单条视频链接
 * 输出：作品列表（文案、赞/评/藏/转、时长、发布时间），按点赞与分享率排序
 *
 * node creator-posts.mjs --input "<...>" [--pages 2] [--top 10] [--json out.json]
 */
import { execFile } from 'node:child_process'
import { readFileSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { promisify } from 'node:util'

const run = promisify(execFile)
const HOME = process.env.DSH_HOME || join(process.env.APPDATA, 'dsh-desktop', 'harness')
const PLUGIN = process.env.DOUYIN_PLUGIN_DIR || 'D:/dsh-plugins/dsh-douyin-scroll'
const SIGNER = join(PLUGIN, 'tools', 'dy-signer.mjs')
const COOKIE_FILE = join(HOME, 'douyin-duty', 'douyin_cookie.txt')
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'

const argv = process.argv.slice(2)
const argOf = (k, d) => { const i = argv.indexOf(k); return i >= 0 ? (argv[i + 1] ?? d) : d }
const INPUT = String(argOf('--input', '')).trim()
const PAGES = Math.max(1, Math.min(15, Number(argOf('--pages', '2')) || 2))
const TOP = Math.max(1, Math.min(50, Number(argOf('--top', '10')) || 10))
const JSON_OUT = argOf('--json', '')
if (!INPUT) { console.error('缺少 --input'); process.exit(2) }

const raw = readFileSync(COOKIE_FILE, 'utf8').trim()
const cookie = raw.startsWith('{') ? JSON.parse(raw).cookies.map((c) => `${c.name}=${c.value}`).join('; ') : raw
const jar = {}
for (const p of cookie.split(';')) { const i = p.indexOf('='); if (i > 0) jar[p.slice(0, i).trim()] = p.slice(i + 1).trim() }
if (!jar.sessionid) { console.error('cookie 里没有 sessionid，先在「设置 → 刷抖音」登录'); process.exit(3) }

async function sign(rel) {
  const { stdout } = await run(process.execPath, [SIGNER, rel], { env: { ...process.env, DY_COOKIES: JSON.stringify(jar) }, maxBuffer: 8 << 20 })
  const i = stdout.indexOf('{\n  "signedUrl"')
  if (i < 0) throw new Error('签名失败：' + stdout.slice(-160))
  return JSON.parse(stdout.slice(i))
}
async function signedGet(rel, referer) {
  const s = await sign(rel)
  const r = await fetch(s.signedUrl, { headers: { 'User-Agent': UA, Cookie: cookie, Referer: referer, ...s.headers } })
  const t = await r.text()
  let json = null
  try { json = JSON.parse(t) } catch { /* 非 JSON */ }
  return { http: r.status, json, text: t }
}

async function resolveSecUid(input) {
  if (/^MS4wLjABAAAA[\w-]{20,}$/.test(input)) return { secUid: input, via: 'sec_uid' }
  let url = input
  if (/v\.douyin\.com/.test(input)) {
    const r = await fetch(input, { headers: { 'User-Agent': UA }, redirect: 'follow' })
    url = r.url || input
  }
  let m = url.match(/\/user\/([^/?#]+)/)
  if (m) return { secUid: m[1], via: 'user_url' }
  m = url.match(/\/video\/(\d+)/) || input.match(/^(\d{15,})$/)
  if (m) {
    const d = await signedGet(`/aweme/v1/web/aweme/detail/?aweme_id=${m[1]}&device_platform=webapp&aid=6383&channel=channel_pc_web`, `https://www.douyin.com/video/${m[1]}`)
    const a = d.json?.aweme_detail?.author
    if (!a?.sec_uid) throw new Error('视频 detail 里没有作者（可能被删/私密）')
    return { secUid: a.sec_uid, via: 'video', nickname: a.nickname, fans: a.follower_count }
  }
  throw new Error('无法解析输入：' + input)
}

async function fetchPosts(secUid, pages) {
  const out = []
  let cursor = 0, hasMore = true
  for (let p = 0; p < pages && hasMore; p++) {
    const rel = `/aweme/v1/web/aweme/post/?device_platform=webapp&aid=6383&channel=channel_pc_web&sec_user_id=${secUid}&max_cursor=${cursor}&count=20&locate_query=false&publish_video_strategy_type=2&cookie_enabled=true&platform=PC`
    const { http, json } = await signedGet(rel, `https://www.douyin.com/user/${secUid}`)
    const list = json?.aweme_list || []
    if (http !== 200 || !list.length) break
    out.push(...list)
    hasMore = Boolean(json?.has_more) && json?.max_cursor !== cursor
    cursor = json?.max_cursor ?? 0
    if (hasMore) await new Promise((r) => setTimeout(r, 1500))
  }
  return out
}

const slim = (a) => {
  const s = a.statistics || {}
  const digg = s.digg_count ?? 0, cmt = s.comment_count ?? 0, col = s.collect_count ?? 0, shr = s.share_count ?? 0
  return {
    aweme_id: a.aweme_id,
    date: new Date((a.create_time || 0) * 1000).toISOString().slice(0, 10),
    duration_s: Math.round((a.video?.duration ?? 0) / 1000),
    digg, comment: cmt, collect: col, share: shr,
    share_rate: digg ? +(shr / digg).toFixed(3) : null,
    collect_rate: digg ? +(col / digg).toFixed(3) : null,
    comment_rate: digg ? +(cmt / digg).toFixed(3) : null,
    desc: (a.desc || '').replace(/\s+/g, ' ').trim(),
    topics: (a.text_extra || []).map((x) => x.hashtag_name).filter(Boolean).slice(0, 6),
    url: `https://www.douyin.com/video/${a.aweme_id}`,
  }
}

try {
  const who = await resolveSecUid(INPUT)
  const posts = await fetchPosts(who.secUid, PAGES)
  if (!posts.length) { console.error('没拿到作品（可能全私密或风控）'); process.exit(4) }
  const items = posts.map(slim)
  const diggs = items.map((x) => x.digg).sort((a, b) => a - b)
  const median = diggs[Math.floor(diggs.length / 2)] ?? 0
  const byDigg = [...items].sort((a, b) => b.digg - a.digg)
  const byShare = items.filter((x) => x.share_rate !== null).sort((a, b) => b.share_rate - a.share_rate)
  const result = {
    ok: true, who, fetched: items.length,
    stats: { median_digg: median, max_digg: byDigg[0]?.digg ?? 0, max_share_rate: byShare[0]?.share_rate ?? null },
    top_by_digg: byDigg.slice(0, TOP),
    top_by_share: byShare.slice(0, TOP),
    all: items,
  }
  if (JSON_OUT) writeFileSync(JSON_OUT, JSON.stringify(result, null, 1), 'utf8')
  const line = (x) => `${x.date} | digg=${x.digg} share=${x.share}(rate=${x.share_rate}) collect_rate=${x.collect_rate} comment_rate=${x.comment_rate} | ${x.desc.slice(0, 34)}`
  console.log('博主：' + (who.nickname || '') + '  ' + who.secUid);
  console.log('抓到 ' + items.length + ' 条 | 中位点赞 ' + median + ' | 最高赞 ' + (byDigg[0] ? byDigg[0].digg : 0));
  console.log('');
  console.log('== 按点赞 Top ==');
  console.log(byDigg.slice(0, TOP).map(line).join(String.fromCharCode(10)));
  console.log('');
  console.log('== 按分享率 Top ==');
  console.log(byShare.slice(0, TOP).map(line).join(String.fromCharCode(10)));
} catch (e) {
  console.error('失败：' + e.message);
  process.exit(1);
}
