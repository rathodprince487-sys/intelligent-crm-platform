import React from 'react';
import { portfolioData } from '../data/portfolioData';
import { GraduationCap, Award, BookOpen } from 'lucide-react';

export const Education = () => {
  return (
    <section id="education" className="py-28 relative" style={{ borderTop: '1px solid var(--border)' }}>
      <div className="max-w-7xl mx-auto px-6">
        <h2 className="font-anton text-5xl sm:text-7xl uppercase mb-16" style={{ color: 'var(--text-primary)' }}>
          Education &<br /><span style={{ color: 'var(--accent)' }}>Certifications</span>
        </h2>

        <div className="grid md:grid-cols-12 gap-16">
          {/* Degrees */}
          <div className="md:col-span-7">
            <div className="flex items-center gap-2 mb-8">
              <GraduationCap className="size-5" style={{ color: 'var(--accent)' }} />
              <span className="text-xs uppercase tracking-widest font-semibold" style={{ color: 'var(--text-muted)' }}>
                Academic Qualifications
              </span>
            </div>

            <div className="space-y-0">
              {portfolioData.education.map((edu, idx) => (
                <div key={idx} className="py-8" style={{ borderTop: '1px solid var(--border)' }}>
                  <div className="flex flex-wrap justify-between items-start gap-4">
                    <div>
                      <h3 className="text-xl sm:text-2xl font-syne font-bold mb-1" style={{ color: 'var(--text-primary)' }}>
                        {edu.degree}
                      </h3>
                      <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                        {edu.institution} · {edu.location}
                      </p>
                      <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
                        {edu.period}
                      </p>
                    </div>
                    <span
                      className="font-anton text-2xl"
                      style={{ color: 'var(--accent)' }}
                    >
                      {edu.score}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Certifications */}
          <div className="md:col-span-5">
            <div className="flex items-center gap-2 mb-8">
              <Award className="size-5" style={{ color: '#22d3ee' }} />
              <span className="text-xs uppercase tracking-widest font-semibold" style={{ color: 'var(--text-muted)' }}>
                Certifications
              </span>
            </div>

            <div className="space-y-0">
              {portfolioData.certifications.map((cert, idx) => (
                <div key={idx} className="py-8" style={{ borderTop: '1px solid var(--border)' }}>
                  <div className="flex items-start gap-4">
                    <div
                      className="size-10 rounded-lg flex items-center justify-center shrink-0"
                      style={{ background: 'rgba(34,211,238,0.1)', border: '1px solid rgba(34,211,238,0.25)', color: '#22d3ee' }}
                    >
                      <BookOpen className="size-5" />
                    </div>
                    <div>
                      <h4 className="font-syne font-bold mb-0.5" style={{ color: 'var(--text-primary)' }}>
                        {cert.title}
                      </h4>
                      <p className="text-xs font-semibold mb-2" style={{ color: '#22d3ee' }}>
                        {cert.provider}
                      </p>
                      <p className="text-xs leading-relaxed" style={{ color: 'var(--text-muted)' }}>
                        {cert.topics}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
