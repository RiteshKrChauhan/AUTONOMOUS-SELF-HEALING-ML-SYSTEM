export default function SectionCard({ title, subtitle, children, action }) {
  return (
    <section className="panel-card section-card">
      <div className="section-head">
        <div>
          <h2 className="section-title">{title}</h2>
          {subtitle ? <p className="section-subtitle">{subtitle}</p> : null}
        </div>
        {action}
      </div>
      {children}
    </section>
  );
}
