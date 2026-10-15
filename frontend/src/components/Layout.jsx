import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { LayoutDashboard, BriefcaseBusiness, FileText, Target, TrendingUp, UserRound, CircleHelp, ShieldCheck, Building2, Users, ClipboardList, Activity, LogOut, Sparkles, Menu, X } from 'lucide-react';
import { useState } from 'react';
import { api } from '../api';

const userLinks = [
  {to:'/app',label:'Overview',icon:LayoutDashboard,end:true},
  {to:'/app/jobs',label:'Find jobs',icon:BriefcaseBusiness},
  {to:'/app/resume',label:'Resume analyzer',icon:FileText},
  {to:'/app/skill-gap',label:'Skill gap',icon:Target},
  {to:'/app/applications',label:'Applications',icon:TrendingUp},
  {to:'/app/profile',label:'My profile',icon:UserRound},
  {to:'/app/help',label:'Help desk',icon:CircleHelp},
];
const adminLinks = [
  {to:'/admin',label:'Admin overview',icon:LayoutDashboard,end:true},
  {to:'/admin/companies',label:'Companies',icon:Building2},
  {to:'/admin/jobs',label:'Job listings',icon:BriefcaseBusiness},
  {to:'/admin/users',label:'Registered users',icon:Users},
  {to:'/admin/applications',label:'Applications',icon:ClipboardList},
  {to:'/admin/activity',label:'Form & activity log',icon:Activity},
  {to:'/admin/help',label:'Support tickets',icon:CircleHelp},
];
export default function Layout({user,setUser,admin=false}) {
  const [mobile,setMobile]=useState(false); const nav=useNavigate(); const links=admin?adminLinks:userLinks;
  async function logout(){try{await api('/api/auth/logout',{method:'POST'});}catch{} localStorage.removeItem('skillmatch_token');localStorage.removeItem('skillmatch_user');setUser(null);nav('/login',{replace:true});}
  return <div className="shell"><aside className={`sidebar ${mobile?'open':''}`}><div className="brand"><span className="brand-mark"><Sparkles size={20}/></span><span>SkillMatch<span className="brand-light"> Pro</span><small>CAREER INTELLIGENCE</small></span><button className="icon-btn mobile-close" onClick={()=>setMobile(false)}><X size={18}/></button></div><div className="workspace-label">WORKSPACE</div><nav>{links.map(({to,label,icon:Icon,end})=><NavLink key={to} to={to} end={end} onClick={()=>setMobile(false)} className={({isActive})=>`nav-link ${isActive?'active':''}`}><Icon size={18}/><span>{label}</span></NavLink>)}</nav><div className="sidebar-bottom"><div className="user-mini"><div className="avatar">{(user?.name||'U').slice(0,1).toUpperCase()}</div><div className="user-mini-text"><b>{user?.name||'Account'}</b><small>{admin?'Administrator':'Candidate'}</small></div></div><button className="logout-btn" onClick={logout}><LogOut size={17}/> Sign out</button></div></aside>{mobile&&<button className="mobile-scrim" onClick={()=>setMobile(false)} aria-label="Close navigation"/>}<main className="main-area"><header className="topbar"><button className="icon-btn menu-toggle" onClick={()=>setMobile(true)}><Menu size={20}/></button><div className="crumb">Workspace <span>/</span> <b>{admin?'Admin console':'Career workspace'}</b></div><div className="topbar-right"><span className="status-dot"/> <span className="online-label">System workspace</span><div className="avatar avatar-sm">{(user?.name||'U').slice(0,1).toUpperCase()}</div></div></header><div className="page-wrap"><Outlet/></div><footer className="footer">© 2026 SkillMatch Pro <span>Build your next opportunity.</span></footer></main></div>
}
