import React from 'react';
import { portfolioData } from '../data/portfolioData';
import { MapPin, Mail } from 'lucide-react';
import { GithubIcon, LinkedinIcon } from './Icons';

export const About = () => {
  return (
    <section id="about-me" className="py-28 relative" style={{ borderTop: '1px solid var(--border)' }}>
      <div className="max-w-7xl mx-auto px-6">

        {/* Top label row */}
        <div className="flex items-center justify-between mb-16">
          <p className="text-xs uppercase tracking-widest" style={{ color: 'var(--text-muted)' }}>
            About Me
          </p>
          <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>
            <span className="size-1.5 rounded-full bg-emerald-500" />
            <span>Status: Available</span>
          </div>
        </div>

        {/* Main grid */}
        <div className="grid md:grid-cols-12 gap-12 lg:gap-20">

          {/* LEFT — profile quick-facts */}
          <div className="md:col-span-4 space-y-8">
            {/* Name card */}
            <div>
              <h2 className="font-anton text-4xl sm:text-5xl uppercase leading-tight mb-2" style={{ color: 'var(--text-primary)' }}>
                Satyajitsinh<br />Rathod
              </h2>
              <p className="text-sm font-medium" style={{ color: 'var(--accent)' }}>
                Project Coordinator & CS Engineer
              </p>
            </div>

            {/* Quick facts */}
            <div className="space-y-0">
              {[
                { label: 'Location',  value: 'Gujarat, India', Icon: MapPin },
                { label: 'Email',     value: portfolioData.personal.email, Icon: Mail },
                { label: 'Degree',    value: 'B.Tech CSE — 7.99 GPA', Icon: null },
                { label: 'Cert',      value: 'SAP Code Unnati', Icon: null },
              ].map(({ label, value, Icon }) => (
                <div key={label} className="flex items-start gap-3 py-4" style={{ borderBottom: '1px solid var(--border)' }}>
                  <div className="w-20 shrink-0 text-[10px] uppercase tracking-wider font-semibold mt-0.5" style={{ color: 'var(--text-muted)' }}>
                    {label}
                  </div>
                  <div className="flex items-center gap-1.5">
                    {Icon && <Icon className="size-3.5 shrink-0" style={{ color: 'var(--accent)' }} />}
                    <span className="text-sm font-medium break-all" style={{ color: 'var(--text-primary)' }}>{value}</span>
                  </div>
                </div>
              ))}
            </div>

            {/* Social links */}
            <div className="flex items-center gap-3">
              <a
                href={portfolioData.personal.githubUrl}
                target="_blank"
                rel="noreferrer"
                className="icon-btn h-9 px-4 rounded-full flex items-center gap-2 text-xs font-semibold"
              >
                <GithubIcon className="size-3.5" />
                <span>GitHub</span>
              </a>
              <a
                href={portfolioData.personal.linkedinUrl}
                target="_blank"
                rel="noreferrer"
                className="icon-btn h-9 px-4 rounded-full flex items-center gap-2 text-xs font-semibold"
              >
                <LinkedinIcon className="size-3.5" />
                <span>LinkedIn</span>
              </a>
            </div>
          </div>

          {/* RIGHT — bio content */}
          <div className="md:col-span-8">
            {/* Bio paragraphs */}
            <div className="space-y-5 text-base sm:text-lg font-light leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
              <p>{portfolioData.personal.aboutParagraph1}</p>
              <p>{portfolioData.personal.aboutParagraph2}</p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
};
