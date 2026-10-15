import {useEffect,useState} from 'react';
import {Navigate,Route,Routes,useLocation} from 'react-router-dom';
import {api} from './api';
import Layout from './components/Layout';
import AuthPage from './pages/AuthPage';
import Overview from './pages/Overview';
import Jobs from './pages/Jobs';
import ResumeAnalyzer from './pages/ResumeAnalyzer';
import Profile from './pages/Profile';
import Applications from './pages/Applications';
import SkillGap from './pages/SkillGap';
import HelpDesk from './pages/HelpDesk';
import AdminOverview from './pages/AdminOverview';
import AdminCompanies from './pages/AdminCompanies';
import AdminJobs from './pages/AdminJobs';
import AdminUsers from './pages/AdminUsers';
import AdminApplications from './pages/AdminApplications';
import AdminActivity from './pages/AdminActivity';
import AdminHelp from './pages/AdminHelp';

function Guard({user,loading,admin,children}){const loc=useLocation();if(loading)return <div className="boot-screen"><div className="brand-mark">SM</div><p>Loading SkillMatch workspace…</p></div>;if(!user)return <Navigate to="/login" replace state={{from:loc.pathname}}/>;if(admin&&user.role!=='admin')return <Navigate to="/app" replace/>;if(!admin&&user.role==='admin')return <Navigate to="/admin" replace/>;return children;}
function UserLayout({user,setUser,admin=false}){return <Layout user={user} setUser={setUser} admin={admin}/>;}
export default function App(){const [user,setUser]=useState(()=>{try{return JSON.parse(localStorage.getItem('skillmatch_user')||'null')}catch{return null}});const [loading,setLoading]=useState(Boolean(localStorage.getItem('skillmatch_token')));useEffect(()=>{if(!localStorage.getItem('skillmatch_token')){setLoading(false);return}api('/api/auth/me').then(u=>{setUser(u);localStorage.setItem('skillmatch_user',JSON.stringify(u))}).catch(()=>{localStorage.removeItem('skillmatch_token');localStorage.removeItem('skillmatch_user');setUser(null)}).finally(()=>setLoading(false))},[]);return <Routes><Route path="/" element={<Navigate to={user?(user.role==='admin'?'/admin':'/app'):'/login'} replace/>}/><Route path="/login" element={user?<Navigate to={user.role==='admin'?'/admin':'/app'} replace/>:<AuthPage setUser={setUser}/>}/><Route path="/register" element={user?<Navigate to="/app" replace/>:<AuthPage setUser={setUser} register/>}/><Route path="/app" element={<Guard user={user} loading={loading}><UserLayout user={user} setUser={setUser}/></Guard>}><Route index element={<Overview user={user}/>}/><Route path="jobs" element={<Jobs/>}/><Route path="resume" element={<ResumeAnalyzer/>}/><Route path="skill-gap" element={<SkillGap/>}/><Route path="applications" element={<Applications/>}/><Route path="profile" element={<Profile/>}/><Route path="help" element={<HelpDesk/>}/></Route><Route path="/admin" element={<Guard user={user} loading={loading} admin><UserLayout user={user} setUser={setUser} admin/></Guard>}><Route index element={<AdminOverview/>}/><Route path="companies" element={<AdminCompanies/>}/><Route path="jobs" element={<AdminJobs/>}/><Route path="users" element={<AdminUsers/>}/><Route path="applications" element={<AdminApplications/>}/><Route path="activity" element={<AdminActivity/>}/><Route path="help" element={<AdminHelp/>}/></Route><Route path="*" element={<Navigate to="/" replace/>}/></Routes>}
