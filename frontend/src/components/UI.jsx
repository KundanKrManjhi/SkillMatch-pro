import { AlertCircle, CheckCircle2, LoaderCircle } from 'lucide-react';
export function PageHeading({eyebrow,title,subtitle,action}){return <div className="page-heading"><div><div className="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{subtitle}</p></div>{action&&<div className="heading-action">{action}</div>}</div>}
export function Notice({error,success}){if(!error&&!success)return null;return <div className={`notice ${error?'notice-error':'notice-success'}`}>{error?<AlertCircle size={17}/>:<CheckCircle2 size={17}/>}<span>{error||success}</span></div>}
export function Loading(){return <div className="loading"><LoaderCircle className="spin" size={22}/> Loading workspace…</div>}
export function Empty({title='Nothing here yet',text='Data will appear here when it is available.'}){return <div className="empty"><div className="empty-icon"><AlertCircle size={22}/></div><b>{title}</b><p>{text}</p></div>}
export function Metric({label,value,detail,icon:Icon,accent='blue'}){return <div className="metric-card"><div className={`metric-icon ${accent}`}>{Icon&&<Icon size={19}/>}</div><div className="metric-label">{label}</div><div className="metric-value">{value??'—'}</div><div className="metric-detail">{detail}</div></div>}
export function Badge({children,tone=''}){return <span className={`badge ${tone}`}>{children}</span>}
export function Field({label,children,hint}){return <label className="field"><span>{label}</span>{children}{hint&&<small>{hint}</small>}</label>}
