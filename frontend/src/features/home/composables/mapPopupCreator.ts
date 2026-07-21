import type { MapObjectCreator } from '@/features/auth/core/auth.types'

function escapeHtml(value: string) {
  return value.replace(/[&<>'"]/g, (character) =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' })[character] ?? character,
  )
}

export function createdByMarkup(creator?: MapObjectCreator | null) {
  if (!creator) {
    return '<section style="margin-top:10px;padding-top:8px;border-top:1px solid #e2e8f0;font-size:11px;color:#64748b;"><strong style="display:block;color:#334155;margin-bottom:4px;">Created by</strong>Unknown user</section>'
  }
  const name = escapeHtml(creator.display_name || creator.username)
  const avatar = creator.avatar
    ? `<img src="${escapeHtml(creator.avatar)}" alt="${name}" style="width:28px;height:28px;object-fit:cover;border-radius:999px;" />`
    : '<span style="width:28px;height:28px;border-radius:999px;background:#e2e8f0;display:inline-block;"></span>'
  const status = creator.current_status
    ? `<span style="display:block;color:#64748b;font-size:10px;">${escapeHtml(creator.current_status)}</span>`
    : ''
  return `<section style="margin-top:10px;padding-top:8px;border-top:1px solid #e2e8f0;font-size:11px;"><strong style="display:block;color:#334155;margin-bottom:5px;">Created by</strong><a href="/profile/${encodeURIComponent(creator.username)}" style="display:flex;align-items:center;gap:7px;color:#2563eb;text-decoration:none;"><span>${avatar}</span><span><span style="display:block;font-weight:600;">${name}</span><span style="display:block;color:#64748b;">@${escapeHtml(creator.username)}</span>${status}</span></a></section>`
}
