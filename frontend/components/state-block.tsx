import { ReactNode } from "react";

interface StateBlockProps {
  title: string;
  description: string;
  action?: ReactNode;
}


export function StateBlock({ title, description, action }: StateBlockProps) {
  return (
    <section className="state-card">
      <h2>{title}</h2>
      <p>{description}</p>
      {action ? <div className="state-action">{action}</div> : null}
    </section>
  );
}
