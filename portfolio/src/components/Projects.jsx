import React, { useState } from 'react';
import { portfolioData } from '../data/portfolioData';
import { ExternalLink } from 'lucide-react';
import { GithubIcon } from './Icons';

const CATS = ['All', 'Fullstack / AI', 'E-Commerce / UX', 'Automation'];

export const Projects = () => {
  const [filter, setFilter] = useState('All');

  const filtered = filter === 'All'
    ? portfolioData.projects
    : portfolioData.projects.filter(p => p.category === filter);

  return (
    <section id="projects" className="py-28 relative" style={{ borderTop: '1px solid var(--border)' }}>
      <div className="max-w-7xl mx-auto px-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-8 mb-16">
          <h2 className="font-anton text-5xl sm:text-7xl uppercase leading-none" style={{ color: 'var(--text-primary)' }}>
            Selected<br />
            <span style={{ color: 'var(--accent)' }}>Projects</span>
          </h2>

          {/* Filter */}
          <div className="flex flex-wrap gap-2">
            {CATS.map(cat => (
              <button
                key={cat}
                onClick={() => setFilter(cat)}
                className="px-4 py-2 rounded-full text-xs font-semibold border transition-all"
                style={filter === cat
                  ? { background: 'var(--btn-bg)', color: 'var(--btn-text)', borderColor: 'var(--btn-bg)' }
                  : { background: 'var(--bg-card)', color: 'var(--text-secondary)', borderColor: 'var(--border)' }
                }
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* Projects — stacked rows, editorial style */}
        <div className="space-y-0">
          {filtered.map((project, i) => (
            <div
              key={project.id}
              className="group grid md:grid-cols-12 gap-6 py-10 items-center transition-all"
              style={{ borderTop: '1px solid var(--border)' }}
            >
              {/* Number */}
              <div className="hidden md:block md:col-span-1">
                <span className="font-anton text-3xl opacity-15" style={{ color: 'var(--text-primary)' }}>
                  {String(i + 1).padStart(2, '0')}
                </span>
              </div>

              {/* Thumbnail */}
              <div className="md:col-span-4 lg:col-span-3 aspect-video rounded-xl overflow-hidden" style={{ background: 'var(--bg-chip)' }}>
                <img
                  src={project.image}
                  alt={project.title}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
              </div>

              {/* Text */}
              <div className="md:col-span-5 lg:col-span-6 space-y-3">
                <div className="flex items-center gap-3">
                  <span className="text-[10px] font-bold uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>
                    {project.category}
                  </span>
                  {project.metrics && (
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500 text-white">
                      {project.metrics}
                    </span>
                  )}
                </div>
                <h3 className="text-xl sm:text-2xl font-syne font-bold transition-colors group-hover:opacity-80" style={{ color: 'var(--text-primary)' }}>
                  {project.title}
                </h3>
                <p className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
                  {project.description}
                </p>
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {project.tags.map(tag => (
                    <span key={tag} className="tag-chip">{tag}</span>
                  ))}
                </div>
              </div>

              {/* Links */}
              <div className="md:col-span-2 flex md:flex-col items-center md:items-end gap-3">
                {project.link && project.link !== '#' && (
                  <a
                    href={project.link}
                    target="_blank"
                    rel="noreferrer"
                    className="btn-primary size-11 rounded-full flex items-center justify-center"
                    title="Visit site"
                  >
                    <ExternalLink className="size-4" />
                  </a>
                )}
                {project.github && project.github !== '#' && (
                  <a
                    href={project.github}
                    target="_blank"
                    rel="noreferrer"
                    className="icon-btn size-11 rounded-full flex items-center justify-center"
                    title="View code"
                  >
                    <GithubIcon className="size-4" />
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
