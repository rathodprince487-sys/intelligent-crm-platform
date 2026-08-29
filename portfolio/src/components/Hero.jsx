import React from 'react';
import { portfolioData } from '../data/portfolioData';
import { ArrowUpRight, Download, CheckCircle2 } from 'lucide-react';

export const Hero = () => {
  return (
    <section id="banner" className="relative min-h-screen flex items-end pb-20 pt-36 overflow-hidden bg-grid-pattern">
      {/* Subtle background orbs */}
      <div className="absolute top-1/3 right-0 w-[600px] h-[600px] rounded-full blur-[120px] pointer-events-none -z-10 opacity-20" style={{ background: 'var(--accent)' }} />

      <div className="max-w-7xl mx-auto px-6 w-full">
        {/* Eyebrow */}
        <p className="text-sm font-medium tracking-widest uppercase mb-6" style={{ color: 'var(--text-muted)' }}>
          — Based in Gujarat, India
        </p>

        {/* Main headline — raw, no pill badges */}
        <h1 className="font-anton uppercase leading-[0.9] tracking-tight mb-10"
          style={{ fontSize: 'clamp(3rem, 10vw, 9rem)', color: 'var(--text-primary)' }}>
          <span style={{ color: 'var(--accent)' }}>Project</span><br />
          Coordinator<br />
          <span className="italic font-syne font-light" style={{ fontSize: '0.55em', color: 'var(--text-secondary)', letterSpacing: '-0.01em' }}>
            & Web Developer
          </span>
        </h1>

        {/* Bottom row */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-10 pt-10" style={{ borderTop: '1px solid var(--border)' }}>
          {/* Bio */}
          <p className="text-base sm:text-lg leading-relaxed max-w-xl" style={{ color: 'var(--text-secondary)' }}>
            I'm <strong style={{ color: 'var(--text-primary)' }}>Satyajitsinh Rathod</strong> — CS Engineer who coordinates software projects, builds web apps, and runs ad campaigns that actually convert. Currently open to full-time roles.
          </p>

          {/* CTAs */}
          <div className="flex flex-wrap gap-3 shrink-0">
            <a href="#contact" className="btn-primary h-12 px-7 rounded-full inline-flex items-center gap-2 text-sm font-bold uppercase tracking-wide group">
              <span>Let's Talk</span>
              <ArrowUpRight className="size-4 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
            </a>
            <a href={`mailto:${portfolioData.personal.email}`} className="btn-secondary h-12 px-7 rounded-full inline-flex items-center gap-2 text-sm font-semibold">
              <span>Email Me</span>
            </a>
          </div>
        </div>

        {/* Tags */}
        <div className="flex flex-wrap items-center gap-6 mt-8 text-xs" style={{ color: 'var(--text-muted)' }}>
          {['CRM & HRMS Automation', 'React & Node.js', 'Facebook Ads — 8+ ROAS'].map(text => (
            <div key={text} className="flex items-center gap-2">
              <span className="size-1.5 rounded-full" style={{ background: 'var(--accent)' }} />
              <span>{text}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
