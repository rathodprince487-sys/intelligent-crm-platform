import React, { useState, useEffect } from 'react';
import { portfolioData } from '../data/portfolioData';
import { Sun, Moon, Menu, X, ArrowUpRight } from 'lucide-react';
import { GithubIcon, LinkedinIcon, GujaratMapIcon } from './Icons';

export const Navbar = ({ theme, toggleTheme }) => {
  const [scrolled, setScrolled] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [currentTime, setCurrentTime] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      const timeStr = now.toLocaleTimeString('en-US', {
        timeZone: 'Asia/Kolkata',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true,
      });
      setCurrentTime(timeStr);
    };

    updateTime();
    const interval = setInterval(updateTime, 10000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 40);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <>
      <header
        className={`fixed top-0 left-0 right-0 z-40 transition-all duration-300 ${scrolled ? 'py-3 navbar-scrolled' : 'py-6'}`}
      >
        <div className="max-w-7xl mx-auto px-6 flex justify-between items-center">
          {/* Logo */}
          <a
            href="#banner"
            onClick={(e) => {
              e.preventDefault();
              window.scrollTo({ top: 0, behavior: 'smooth' });
            }}
            className="flex items-center gap-3 group cursor-pointer"
            title="Back to Top"
          >
            <div
              className="size-10 rounded-full flex items-center justify-center font-anton text-lg transition-all duration-300 group-hover:scale-110 group-hover:rotate-6 group-active:scale-95"
              style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', color: 'var(--accent)' }}
            >
              SR.
            </div>
            <div className="flex flex-col">
              <span className="font-syne font-bold tracking-wider text-sm transition-colors group-hover:text-[var(--accent)]" style={{ color: 'var(--text-primary)' }}>SATYAJITSINH</span>
              <span className="text-[10px] tracking-widest uppercase" style={{ color: 'var(--text-muted)' }}>Project Coordinator</span>
            </div>
          </a>

          {/* Right Controls */}
          <div className="flex items-center gap-4">
            {/* Live Location & Time Widget with Gujarat Map Icon */}
            <div className="hidden sm:flex items-center gap-2 text-xs font-mono tracking-wider uppercase px-3.5 py-1.5 rounded-full" style={{ background: 'var(--bg-chip)', border: '1px solid var(--border)' }}>
              <GujaratMapIcon className="size-4 shrink-0" />
              <span style={{ color: 'var(--text-secondary)' }}>Gujarat, IN</span>
              <span style={{ color: 'var(--text-muted)' }}>•</span>
              <span className="font-bold" style={{ color: 'var(--text-primary)' }}>{currentTime || '03:06 PM'} IST</span>
            </div>

            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="size-10 rounded-full flex items-center justify-center transition-all icon-btn"
              title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
              aria-label="Toggle Theme"
            >
              {theme === 'dark'
                ? <Sun className="size-4" style={{ color: 'var(--accent)' }} />
                : <Moon className="size-4" style={{ color: 'var(--text-primary)' }} />
              }
            </button>

            {/* Menu Button */}
            <button
              onClick={() => setIsMenuOpen(v => !v)}
              className="size-10 rounded-full flex items-center justify-center transition-all icon-btn"
              aria-label="Toggle Menu"
            >
              {isMenuOpen
                ? <X className="size-5" style={{ color: 'var(--text-primary)' }} />
                : <Menu className="size-5" style={{ color: 'var(--text-primary)' }} />
              }
            </button>
          </div>
        </div>
      </header>

      {/* Fullscreen Mobile / Navigation Drawer */}
      <div
        className={`fixed inset-0 z-50 flex flex-col justify-between p-8 sm:p-16 transition-all duration-500 ease-in-out ${
          isMenuOpen ? 'opacity-100 pointer-events-auto translate-y-0' : 'opacity-0 pointer-events-none -translate-y-8'
        }`}
        style={{ background: 'var(--drawer-bg)', color: 'var(--text-primary)' }}
      >
        {/* Drawer Header */}
        <div className="flex justify-between items-center">
          <span className="font-anton text-2xl" style={{ color: 'var(--accent)' }}>SR.</span>
          <button
            onClick={() => setIsMenuOpen(false)}
            className="size-12 rounded-full flex items-center justify-center icon-btn"
          >
            <X className="size-6" />
          </button>
        </div>

        {/* Navigation Links */}
        <nav className="flex flex-col gap-6 my-auto max-w-xl">
          {[
            { label: 'About',      href: '#about-me' },
            { label: 'Tech Stack', href: '#my-stack' },
            { label: 'Experience', href: '#experience' },
            { label: 'Projects',   href: '#projects' },
            { label: 'Education',  href: '#education' },
            { label: 'Contact',    href: '#contact' },
          ].map((item, idx) => (
            <a
              key={item.label}
              href={item.href}
              onClick={() => setIsMenuOpen(false)}
              className="font-anton text-4xl sm:text-6xl uppercase tracking-wider flex items-center gap-4 group transition-transform hover:translate-x-3"
              style={{ color: 'var(--text-primary)' }}
            >
              <span className="text-xs font-mono font-normal opacity-30 group-hover:opacity-100" style={{ color: 'var(--accent)' }}>
                0{idx + 1}
              </span>
              <span>{item.label}</span>
            </a>
          ))}
        </nav>

        {/* Drawer Footer */}
        <div className="pt-8 border-t flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4" style={{ borderColor: 'var(--border)' }}>
          <p className="text-sm font-mono" style={{ color: 'var(--text-muted)' }}>
            {portfolioData.personal.email}
          </p>
          <div className="flex items-center gap-4">
            <a
              href={portfolioData.personal.githubUrl}
              target="_blank"
              rel="noreferrer"
              className="size-10 rounded-full flex items-center justify-center icon-btn"
            >
              <GithubIcon className="size-5" />
            </a>
            <a
              href={portfolioData.personal.linkedinUrl}
              target="_blank"
              rel="noreferrer"
              className="size-10 rounded-full flex items-center justify-center icon-btn"
            >
              <LinkedinIcon className="size-5" />
            </a>
          </div>
        </div>
      </div>
    </>
  );
};
