import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import {
  ArrowRight,
  BriefcaseBusiness,
  CheckCircle2,
  FileText,
  ShieldCheck,
  Sparkles,
  Target,
} from 'lucide-react';

import { api, json } from '../api';
import { Notice, Field } from '../components/UI';

export default function AuthPage({ setUser, register = false }) {
  const [mode, setMode] = useState('user');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const nav = useNavigate();

  async function submit(e) {
    e.preventDefault();

    if (busy) return;

    setError('');

    const cleanEmail = email.trim().toLowerCase();

    if (register && name.trim().length < 2) {
      setError('Please enter your full name.');
      return;
    }

    if (!cleanEmail || !password) {
      setError('Please enter your email and password.');
      return;
    }

    if (register && password.length < 8) {
      setError('Password must contain at least 8 characters.');
      return;
    }

    setBusy(true);

    try {
      const endpoint = register
        ? '/api/auth/register'
        : '/api/auth/login';

      const payload = register
        ? {
            name: name.trim(),
            email: cleanEmail,
            password,
          }
        : {
            email: cleanEmail,
            password,
          };

      const result = await api(endpoint, json('POST', payload));

      // Validate the authentication response.
      if (!result || !result.user || !result.access_token) {
        throw new Error(
          'Invalid server response. Please check the backend API.'
        );
      }

      // Check the selected account role.
      if (mode === 'admin' && result.user.role !== 'admin') {
        throw new Error(
          'This account is not an administrator. Please use an admin account.'
        );
      }

      if (mode === 'user' && result.user.role === 'admin') {
        throw new Error(
          'This is an admin account. Please select Admin login.'
        );
      }

      // Save session only after successful authentication.
      localStorage.setItem(
        'skillmatch_token',
        result.access_token
      );

      localStorage.setItem(
        'skillmatch_user',
        JSON.stringify(result.user)
      );

      setUser(result.user);

      // Redirect according to the authenticated role.
      nav(
        result.user.role === 'admin' ? '/admin' : '/app',
        { replace: true }
      );
    } catch (err) {
      console.error('Authentication error:', err);

      setError(
        err?.message ||
          'Unable to authenticate. Please try again.'
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="auth-screen">
      <div className="auth-left">
        <div className="auth-brand">
          <span className="brand-mark">
            <Sparkles size={20} />
          </span>

          SkillMatch <span>Pro</span>
        </div>

        <div className="auth-hero">
          <div className="hero-pill">
            <span className="status-dot" />
            CAREER INTELLIGENCE PLATFORM
          </div>

          <h1>
            Your next role starts with a{' '}
            <em>stronger profile.</em>
          </h1>

          <p>
            Understand your resume, uncover skill gaps, and
            find opportunities that fit your goals.
          </p>

          <div className="auth-benefits">
            <div>
              <span>
                <FileText size={18} />
              </span>

              <div>
                <b>Resume intelligence</b>
                <small>
                  Score, feedback and actionable improvements
                </small>
              </div>
            </div>

            <div>
              <span>
                <Target size={18} />
              </span>

              <div>
                <b>Smarter job matching</b>
                <small>See where your skills line up</small>
              </div>
            </div>

            <div>
              <span>
                <BriefcaseBusiness size={18} />
              </span>

              <div>
                <b>Application tracking</b>
                <small>
                  Keep every opportunity in one place
                </small>
              </div>
            </div>
          </div>
        </div>

        <div className="auth-foot">
          Designed for your next career move
          <span>•</span> SkillMatch Pro 2.0
        </div>
      </div>

      <div className="auth-right">
        <div className="auth-form-wrap">
          <div className="auth-kicker">
            WELCOME {register ? 'ABOARD' : 'BACK'}
          </div>

          <h2>
            {register
              ? 'Create your account'
              : 'Sign in to your workspace'}
          </h2>

          <p className="auth-subtitle">
            {register
              ? 'Build your profile and find your best-fit roles.'
              : 'Pick up where your career journey left off.'}
          </p>

          {!register && (
            <div className="role-switch">
              <button
                className={mode === 'user' ? 'selected' : ''}
                onClick={() => {
                  setMode('user');
                  setError('');
                }}
                type="button"
              >
                <BriefcaseBusiness size={16} />
                User
              </button>

              <button
                className={mode === 'admin' ? 'selected' : ''}
                onClick={() => {
                  setMode('admin');
                  setError('');
                }}
                type="button"
              >
                <ShieldCheck size={16} />
                Admin
              </button>
            </div>
          )}

          <Notice error={error} />

          <form onSubmit={submit} className="form-stack">
            {register && (
              <Field label="Full name">
                <input
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Kundan Kumar"
                  minLength={2}
                  required
                  autoComplete="name"
                />
              </Field>
            )}

            <Field label="Email address">
              <input
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder={
                  mode === 'admin'
                    ? 'admin@skillmatch.local'
                    : 'you@example.com'
                }
                type="email"
                required
                autoComplete="email"
              />
            </Field>

            <Field
              label="Password"
              hint={
                register
                  ? 'Use at least 8 characters.'
                  : 'Your password is case-sensitive.'
              }
            >
              <input
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                type="password"
                minLength={register ? 8 : 1}
                required
                autoComplete={
                  register ? 'new-password' : 'current-password'
                }
              />
            </Field>

            <button
              className="btn btn-primary btn-full"
              type="submit"
              disabled={busy}
            >
              {busy
                ? 'Please wait...'
                : register
                  ? 'Create free account'
                  : 'Sign in'}

              {!busy && <ArrowRight size={17} />}
            </button>
          </form>

          {!register && mode === 'admin' && (
            <div className="auth-hint">
              <ShieldCheck size={16} />

              <span>
                Admin credentials are configured in{' '}
                <code>backend/.env</code>. Use the credentials
                configured for your backend.
              </span>
            </div>
          )}

          <div className="auth-switch">
            {register
              ? 'Already have an account?'
              : 'New to SkillMatch?'}{' '}

            <Link to={register ? '/login' : '/register'}>
              {register ? 'Sign in' : 'Create an account'}
            </Link>
          </div>

          <div className="privacy-note">
            <CheckCircle2 size={15} />

            Your profile and resume analysis stay in your
            project database.
          </div>
        </div>
      </div>
    </div>
  );
}