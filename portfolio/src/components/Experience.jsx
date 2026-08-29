import React from 'react';
import { portfolioData } from '../data/portfolioData';
import { Calendar, MapPin, CheckCircle, ExternalLink } from 'lucide-react';

export const Experience = () => {
  return (
    <section id="experience" className="py-28 relative" style={{ borderTop: '1px solid var(--border)' }}>
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-16">
          <h2 className="font-anton text-5xl sm:text-7xl uppercase" style={{ color: 'var(--text-primary)' }}>
            Work<br /><span style={{ color: 'var(--accent)' }}>Experience</span>
          </h2>
          <p className="text-sm max-w-xs" style={{ color: 'var(--text-muted)' }}>
            Where I've put skills to work — professionally.
          </p>
        </div>

        <div className="space-y-0">
          {portfolioData.experiences.map((exp, i) => (
            <div
              key={exp.id}
              className="group grid md:grid-cols-12 gap-6 py-10 transition-colors"
              style={{ borderTop: '1px solid var(--border)' }}
            >
              {/* Index + type */}
              <div className="md:col-span-2 flex md:flex-col items-center md:items-start gap-3">
                <span className="font-anton text-4xl opacity-20" style={{ color: 'var(--text-primary)' }}>
                  {String(i + 1).padStart(2, '0')}
                </span>
                <span
                  className="px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider"
                  style={{ background: 'var(--accent-muted)', color: 'var(--text-accent)' }}
                >
                  {exp.type}
                </span>
              </div>

              {/* Content */}
              <div className="md:col-span-7 space-y-4">
                <div>
                  <h3 className="text-xl sm:text-2xl font-syne font-bold" style={{ color: 'var(--text-primary)' }}>
                    {exp.role}
                  </h3>
                  <div className="flex items-center gap-1.5 mt-1">
                    <span style={{ color: 'var(--text-muted)' }}>at</span>
                    {exp.companyUrl ? (
                      <a
                        href={exp.companyUrl}
                        target="_blank"
                        rel="noreferrer"
                        className="font-semibold inline-flex items-center gap-1 hover:underline"
                        style={{ color: 'var(--accent)' }}
                      >
                        {exp.company}
                        <ExternalLink className="size-3.5" />
                      </a>
                    ) : (
                      <span className="font-semibold" style={{ color: 'var(--text-secondary)' }}>{exp.company}</span>
                    )}
                  </div>
                </div>

                <p className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
                  {exp.description}
                </p>

                <ul className="space-y-2">
                  {exp.highlights.map((item, j) => (
                    <li key={j} className="flex items-start gap-2.5 text-sm" style={{ color: 'var(--text-secondary)' }}>
                      <CheckCircle className="size-3.5 shrink-0 mt-1" style={{ color: 'var(--accent)' }} />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>

                <div className="flex flex-wrap gap-1.5 pt-2">
                  {exp.technologies.map(tech => (
                    <span key={tech} className="tag-chip">{tech}</span>
                  ))}
                </div>
              </div>

              {/* Meta */}
              <div className="md:col-span-3 flex md:flex-col gap-3 text-xs" style={{ color: 'var(--text-muted)' }}>
                <div className="flex items-center gap-1.5">
                  <Calendar className="size-3.5 shrink-0" />
                  <span>{exp.period}</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <MapPin className="size-3.5 shrink-0" />
                  <span>{exp.location}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
