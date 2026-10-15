import { useEffect, useState } from 'react';

import {
  UploadCloud,
  FileText,
  CheckCircle2,
  AlertTriangle,
  Lightbulb,
  RefreshCw,
} from 'lucide-react';

import { api } from '../api';

import {
  PageHeading,
  Notice,
  Badge,
} from '../components/UI';

const MIN = 20 * 1024;
const MAX = 10 * 1024 * 1024;

export default function ResumeAnalyzer() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  // Load the latest resume analysis.
  useEffect(() => {
    let active = true;

    async function loadLatestResume() {
      try {
        const response = await api('/api/resumes/latest');

        if (
          active &&
          response &&
          (response.filename || response.score !== undefined)
        ) {
          setResult(response);
        }
      } catch {
        // No previous resume is okay.
      }
    }

    loadLatestResume();

    return () => {
      active = false;
    };
  }, []);

  // Validate and upload a PDF resume.
  async function upload(e) {
    e.preventDefault();
    setError('');

    if (!file) {
      setError('Please choose a PDF resume first.');
      return;
    }

    const isPdf =
      file.type === 'application/pdf' ||
      file.name.toLowerCase().endsWith('.pdf');

    if (!isPdf) {
      setError('Only PDF resume files are allowed.');
      return;
    }

    if (file.size < MIN) {
      setError('PDF must be at least 20 KB.');
      return;
    }

    if (file.size > MAX) {
      setError('PDF must be 10 MB or smaller.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setBusy(true);

    try {
      const response = await api('/api/resumes/upload', {
        method: 'POST',
        body: formData,
      });

      setResult(response);
      setFile(null);
      setError('');
    } catch (err) {
      setError(
        err?.message || 'Resume upload failed. Please try again.'
      );
    } finally {
      setBusy(false);
    }
  }

  const score = Math.max(
    0,
    Math.min(100, Number(result?.score) || 0)
  );

  const scoreLabel =
    score >= 75
      ? 'Strong start'
      : score >= 50
        ? 'Room to improve'
        : 'Needs attention';

  const scoreTone =
    score >= 75
      ? 'good'
      : score >= 50
        ? 'warn'
        : 'danger';

  return (
    <>
      <PageHeading
        eyebrow="RESUME INTELLIGENCE"
        title="Resume Analyzer"
        subtitle="Upload your resume to review its score, discover missing sections, identify skills and get practical improvement suggestions."
      />

      <Notice error={error} />

      <div className="resume-layout">
        {/* Upload Resume */}
        <section className="panel upload-panel">
          <div className="panel-head">
            <div>
              <div className="eyebrow">
                UPLOAD OR REPLACE
              </div>

              <h3>Your latest resume</h3>
            </div>

            <FileText
              size={20}
              className="muted-icon"
            />
          </div>

          <form onSubmit={upload}>
            <label className="upload-zone">
              <input
                type="file"
                accept=".pdf,application/pdf"
                disabled={busy}
                onChange={(e) => {
                  const selectedFile =
                    e.target.files?.[0] || null;

                  setFile(selectedFile);
                  setError('');
                }}
              />

              <span className="upload-icon">
                <UploadCloud size={26} />
              </span>

              <b>
                {file
                  ? file.name
                  : 'Choose your resume PDF'}
              </b>

              <p>
                PDF format only · Minimum 400 KB ·
                Maximum 10 MB
              </p>

              <span className="btn btn-secondary btn-sm">
                Choose PDF
              </span>
            </label>

            {file && (
              <div className="selected-file">
                <FileText size={17} />

                <span>{file.name}</span>

                <b>
                  {(file.size / (1024 * 1024)).toFixed(2)} MB
                </b>
              </div>
            )}

            <button
              type="submit"
              className="btn btn-primary btn-full"
              disabled={busy}
            >
              {busy
                ? 'Analyzing PDF...'
                : result
                  ? 'Analyze replacement resume'
                  : 'Analyze my resume'}

              <RefreshCw size={16} />
            </button>
          </form>

          <div className="upload-rules">
            <span>
              <CheckCircle2 size={15} />
              PDF validation
            </span>

            <span>
              <CheckCircle2 size={15} />
              Authenticated upload
            </span>

            <span>
              <CheckCircle2 size={15} />
              Resume replacement
            </span>
          </div>
        </section>

        {/* Analysis Report */}
        {result ? (
          <section className="panel score-panel">
            <div className="panel-head">
              <div>
                <div className="eyebrow">
                  LATEST ANALYSIS
                </div>

                <h3>
                  {result.filename || 'Resume report'}
                </h3>
              </div>

              <Badge tone={scoreTone}>
                {scoreLabel}
              </Badge>
            </div>

            {/* Resume Score */}
            <div className="score-overview">
              <div
                className="score-ring"
                style={{
                  '--score': `${score}%`,
                }}
              >
                <div>
                  <strong>{score}</strong>
                  <span>/100</span>
                </div>
              </div>

              <div>
                <h2>Resume readiness</h2>

                <p>
                  Your score is based on the analysis
                  returned by the backend. It does not
                  guarantee ATS ranking or hiring outcomes.
                </p>

                <div className="score-mini">
                  <span>
                    {result.word_count || 0} words
                  </span>

                  <span>
                    {result.skills?.length || 0} detected skills
                  </span>
                </div>
              </div>
            </div>

            {/* Section Checklist */}
            <h4 className="section-title">
              Section checklist
            </h4>

            <div className="check-grid">
              {Object.entries(result.sections || {}).map(
                ([name, found]) => (
                  <div
                    key={name}
                    className="check-item"
                  >
                    {found ? (
                      <CheckCircle2
                        size={17}
                        className="success-icon"
                      />
                    ) : (
                      <AlertTriangle
                        size={17}
                        className="warning-icon"
                      />
                    )}

                    <span>
                      {name.charAt(0).toUpperCase() +
                        name.slice(1)}
                    </span>

                    <b>
                      {found ? 'Found' : 'Review'}
                    </b>
                  </div>
                )
              )}

              {Object.keys(result.sections || {}).length ===
                0 && (
                <p className="muted">
                  No section checklist is available.
                </p>
              )}
            </div>

            {/* Detected Skills */}
            <h4 className="section-title">
              Detected skills
            </h4>

            <div className="skill-chips">
              {(result.skills || []).map((skill) => (
                <span key={skill}>{skill}</span>
              ))}

              {!result.skills?.length && (
                <p className="muted">
                  No supported skills were detected.
                  Add a clearly labelled skills section
                  to your resume.
                </p>
              )}
            </div>

            {/* Improvement Suggestions */}
            <h4 className="section-title">
              Improvement plan
            </h4>

            <div className="suggestion-list">
              {(result.suggestions || []).map(
                (suggestion, index) => (
                  <div key={index}>
                    <Lightbulb size={17} />

                    <span>{suggestion}</span>
                  </div>
                )
              )}

              {!result.suggestions?.length && (
                <p className="muted">
                  No improvement suggestions are
                  available yet.
                </p>
              )}
            </div>
          </section>
        ) : (
          <section className="panel empty-report">
            <div className="empty-illustration">
              <FileText size={32} />
            </div>

            <h3>
              Your resume report will appear here
            </h3>

            <p>
              Upload a PDF to review your score,
              detected skills, missing sections and
              improvement suggestions.
            </p>

            <div className="report-preview">
              <span>Resume score</span>

              <b>— / 100</b>

              <div className="skeleton-bar" />

              <div className="skeleton-bar short" />
            </div>
          </section>
        )}
      </div>
    </>
  );
}