function WidgetCard({ title, actions, children }) {
  return (
    <article className="widget">
      <header className="card-header">
        <h3>{title}</h3>
        <div className="widget-actions">{actions}</div>
      </header>
      <div>{children}</div>
    </article>
  );
}

export default WidgetCard;
