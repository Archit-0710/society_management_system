export function PlaceholderPage({ title, description }) {
  return <section className="placeholder-page" aria-labelledby="page-title"><p className="eyebrow">Phase 1</p><h1 id="page-title">{title}</h1><p>{description}</p></section>
}
