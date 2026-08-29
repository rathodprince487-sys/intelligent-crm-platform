import React, { useState } from 'react';
import { portfolioData } from '../data/portfolioData';
import { OpenAIIcon, ShopifyIcon } from './Icons';

// All icons via reliable CDN sources or inline SVGs
const LOGO_MAP = {
  'js':           { src: 'https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/javascript/javascript-original.svg',   color: '#F7DF1E' },
  'react':        { src: 'https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/react/react-original.svg',             color: '#61DAFB' },
  'html-css':     { src: 'https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/html5/html5-original.svg',             color: '#E34F26' },
  'tailwind':     { src: 'https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/tailwindcss/tailwindcss-original.svg', color: '#06B6D4' },
  'python':       { src: 'https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/python/python-original.svg',           color: '#3776AB' },
  'node':         { src: 'https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/nodejs/nodejs-original.svg',           color: '#339933' },
  'sql':          { src: 'https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/mysql/mysql-original.svg',             color: '#4479A1' },
  'rest':         { src: 'https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/fastapi/fastapi-original.svg',         color: '#059669' },
  'n8n':          { src: 'https://cdn.simpleicons.org/n8n/EA4B71',                                                         color: '#EA4B71' },
  'ai-tools':     { Component: OpenAIIcon,                                                                                  color: '#00a67e' },
  'shopify':      { Component: ShopifyIcon,                                                                                 color: '#95BF47' },
  'git':          { src: 'https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/git/git-original.svg',                color: '#F05028' },
  'facebook-ads': { src: 'https://cdn.simpleicons.org/meta/0082FB',                                                        color: '#0082FB' },
  'crm-hrms':     { src: 'https://cdn.simpleicons.org/hubspot/FF7A59',                                                     color: '#FF7A59' },
};

const GROUPS = [
  { id: '01', title: 'Frontend',          cat: 'Frontend',          color: '#61DAFB' },
  { id: '02', title: 'Backend & DB',      cat: 'Backend & DB',      color: '#339933' },
  { id: '03', title: 'Automation & AI',   cat: 'Automation & AI',   color: '#EA4B71' },
  { id: '04', title: 'Marketing & CRM',  cat: 'Growth & Marketing', color: '#1877F2' },
];

const FILTERS = [
  { id: 'All',                label: 'All' },
  { id: 'Frontend',           label: 'Frontend' },
  { id: 'Backend & DB',       label: 'Backend' },
  { id: 'Automation & AI',    label: 'Automation' },
  { id: 'Growth & Marketing', label: 'Marketing' },
];

export const TechStack = () => {
  const [active, setActive] = useState('All');
  const [hovered, setHovered] = useState(null);

  const visibleGroups = active === 'All'
    ? GROUPS
    : GROUPS.filter(g => g.cat === active);

  return (
    <section id="my-stack" className="py-28 relative" style={{ borderTop: '1px solid var(--border)' }}>
      <div className="max-w-7xl mx-auto px-6">

        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-16">
          <h2 className="font-anton text-5xl sm:text-7xl uppercase leading-none" style={{ color: 'var(--text-primary)' }}>
            Tech<br /><span style={{ color: 'var(--accent)' }}>Stack</span>
          </h2>

          {/* Filter pills */}
          <div className="flex flex-wrap gap-2">
            {FILTERS.map(f => (
              <button
                key={f.id}
                onClick={() => setActive(f.id)}
                className="px-4 py-2 rounded-full text-xs font-semibold border transition-all"
                style={active === f.id
                  ? { background: 'var(--btn-bg)', color: 'var(--btn-text)', borderColor: 'var(--btn-bg)' }
                  : { background: 'var(--bg-card)', color: 'var(--text-secondary)', borderColor: 'var(--border)' }
                }
              >
                {f.label}
              </button>
            ))}
          </div>
        </div>

        {/* Skill groups */}
        <div className="space-y-0">
          {visibleGroups.map((group) => {
            const skills = portfolioData.skillsList.filter(s => s.category === group.cat);
            return (
              <div
                key={group.title}
                className="grid sm:grid-cols-12 gap-6 py-10 items-center"
                style={{ borderTop: '1px solid var(--border)' }}
              >
                {/* Category label */}
                <div className="sm:col-span-4 lg:col-span-3">
                  <h3 className="font-anton text-2xl sm:text-3xl uppercase tracking-wide leading-none" style={{ color: 'var(--text-primary)' }}>
                    {group.title}
                  </h3>
                </div>

                {/* Logo icons */}
                <div className="sm:col-span-8 lg:col-span-9 flex flex-wrap gap-3.5">
                  {skills.map(skill => {
                    const logo = LOGO_MAP[skill.id];
                    const isHovered = hovered === skill.id;

                    return (
                      <div
                        key={skill.id}
                        className="relative"
                        onMouseEnter={() => setHovered(skill.id)}
                        onMouseLeave={() => setHovered(null)}
                        onTouchStart={() => setHovered(prev => prev === skill.id ? null : skill.id)}
                      >
                        {/* Cool Glassmorphic Logo Tile */}
                        <div
                          className="size-16 rounded-2xl flex items-center justify-center cursor-default transition-all duration-300"
                          style={{
                            background: isHovered
                              ? `radial-gradient(circle at center, ${skill.color}22 0%, var(--bg-card) 100%)`
                              : 'var(--bg-card)',
                            border: `1px solid ${isHovered ? skill.color + '70' : 'var(--border)'}`,
                            transform: isHovered ? 'translateY(-5px) scale(1.06)' : 'translateY(0) scale(1)',
                            boxShadow: isHovered
                              ? `0 14px 28px -6px ${skill.color}40, inset 0 0 12px ${skill.color}15`
                              : 'var(--card-shadow)',
                            backdropFilter: 'blur(10px)',
                            WebkitBackdropFilter: 'blur(10px)',
                          }}
                        >
                          {logo?.Component ? (
                            <div style={{ color: logo.color }}>
                              <logo.Component className="size-8 transition-transform duration-300" style={{ transform: isHovered ? 'scale(1.1)' : 'scale(1)' }} />
                            </div>
                          ) : logo?.src ? (
                            <img
                              src={logo.src}
                              alt={skill.name}
                              className="size-8 object-contain transition-transform duration-300"
                              style={{ transform: isHovered ? 'scale(1.1)' : 'scale(1)' }}
                              loading="lazy"
                              onError={e => {
                                e.currentTarget.style.display = 'none';
                                if (e.currentTarget.nextSibling) {
                                  e.currentTarget.nextSibling.style.display = 'flex';
                                }
                              }}
                            />
                          ) : null}
                          {/* Text fallback (hidden unless img errors or no logo) */}
                          <span
                            className="text-[10px] font-black leading-none text-center"
                            style={{ display: (logo?.src || logo?.Component) ? 'none' : 'flex', color: skill.color }}
                          >
                            {skill.name.slice(0, 3).toUpperCase()}
                          </span>
                        </div>

                        {/* Tooltip */}
                        <div
                          className="absolute bottom-full left-1/2 mb-3 z-50 pointer-events-none"
                          style={{
                            transform: `translateX(-50%) translateY(${isHovered ? '0px' : '6px'})`,
                            opacity: isHovered ? 1 : 0,
                            transition: 'opacity 0.18s ease, transform 0.18s ease',
                          }}
                        >
                          <div
                            className="rounded-xl px-3 py-2 text-center whitespace-nowrap shadow-xl"
                            style={{
                              background: 'var(--bg-surface)',
                              border: `1px solid var(--border)`,
                              minWidth: '90px',
                            }}
                          >
                            <p className="text-xs font-bold" style={{ color: 'var(--text-primary)' }}>
                              {skill.name}
                            </p>
                            <p className="text-[10px] mt-0.5 font-semibold" style={{ color: skill.color }}>
                              {skill.level}
                            </p>
                          </div>
                          {/* Arrow */}
                          <div
                            className="size-2 rotate-45 mx-auto -mt-[5px]"
                            style={{
                              background: 'var(--bg-surface)',
                              borderRight: '1px solid var(--border)',
                              borderBottom: '1px solid var(--border)',
                            }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>

      </div>
    </section>
  );
};
