import React, { useState, useEffect, useRef } from 'react';
import { portfolioData } from '../data/portfolioData';
import {
  X, ArrowRight, User, Briefcase, Layers, Sparkles, PhoneCall,
  Search, Bot, CheckCircle, ExternalLink
} from 'lucide-react';
import { GithubIcon, LinkedinIcon } from './Icons';

export const SRModal = ({ isOpen, onClose }) => {
  const [query, setQuery] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [activeTab, setActiveTab] = useState('home');
  const chatEndRef = useRef(null);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);

  if (!isOpen) return null;

  const handleAsk = (userQuery) => {
    const q = (userQuery || query).trim().toLowerCase();
    if (!q) return;

    let answer = "";

    if (q.includes('skill') || q.includes('tech') || q.includes('stack') || q.includes('react') || q.includes('python')) {
      answer = `Satyajitsinh's core tech stack includes:\n• Frontend: JavaScript (ES6+), React.js, HTML5, CSS3, Tailwind CSS\n• Backend & DB: Python, Node.js, Express, SQL, SQLite, RESTful APIs\n• Automation & AI: n8n, AI Prompting & LLMs, Shopify API, Git & GitHub\n• Marketing: Facebook Ad Manager (8+ ROAS), CRM & HRMS Workflows.`;
    } else if (q.includes('project') || q.includes('work') || q.includes('crm') || q.includes('verymiss') || q.includes('velvetnova')) {
      answer = `Here are Satyajitsinh's top projects:\n1. AI-Powered CRM & Automation Platform (Streamlit, Playwright, n8n, Python)\n2. Velvetnova.in (E-Commerce Growth Strategy & UX)\n3. Verymiss.in (Shopify Inventory Order Automation - Saved 20+ hrs/week)\n4. SHDPIXEL Software Project Coordination & CRM/HRMS workflows.`;
    } else if (q.includes('experience') || q.includes('job') || q.includes('intern') || q.includes('shdpixel')) {
      answer = `Experience Summary:\n• Project Coordinator Intern at SHDPIXEL (Nov 2025 – Mar 2026): Managed software sprint execution, task tracking, CRM/HRMS lead automation, and cross-functional team workflows.\n• Facebook Marketing & Campaign Strategist (2024 – Present): Managed high-ROI paid ad campaigns delivering an 8+ ROAS.`;
    } else if (q.includes('contact') || q.includes('email') || q.includes('hire') || q.includes('phone') || q.includes('reach')) {
      answer = `Get in touch with Satyajitsinh:\n• Email: ${portfolioData.personal.email}\n• Phone: ${portfolioData.personal.phone}\n• Location: ${portfolioData.personal.location}\n• Status: Available for Full-Time & Freelance roles!`;
    } else if (q.includes('education') || q.includes('degree') || q.includes('gpa') || q.includes('college')) {
      answer = `Education:\n• B.Tech in Computer Science & Engineering (7.99 GPA) from Silver Oak College of Engineering & Technology, Ahmedabad (2021 – 2025).\n• Certification: SAP Code Unnati — Emerging Tech (AI, Cloud, Analytics).`;
    } else {
      answer = `Hi! I'm Satyajitsinh Rathod — a CS Engineer & Project Coordinator based in Gujarat, India. I specialize in software project coordination, full-stack web development, and digital automation flows. Ask me about my skills, projects, experience, or education!`;
    }

    setChatHistory(prev => [
      ...prev,
      { sender: 'user', text: userQuery || query },
      { sender: 'bot', text: answer }
    ]);
    setQuery('');
    setActiveTab('chat');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    handleAsk(query);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 overflow-y-auto">
      {/* Dimmed backdrop with blur */}
      <div
        className="fixed inset-0 bg-black/70 backdrop-blur-xl transition-opacity animate-fade-in"
        onClick={onClose}
      />

      {/* Main Modal Container */}
      <div
        className="relative w-full max-w-2xl rounded-3xl p-6 sm:p-8 shadow-2xl z-10 transition-all duration-300 transform scale-100 my-auto border"
        style={{
          background: 'var(--bg-surface)',
          borderColor: 'var(--border)',
          color: 'var(--text-primary)',
        }}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 size-10 rounded-full flex items-center justify-center icon-btn transition-transform hover:rotate-90"
          aria-label="Close Modal"
        >
          <X className="size-5" />
        </button>

        {/* Top Header & Avatar */}
        <div className="flex flex-col items-center text-center mt-2 mb-6">
          {/* Logo Badge */}
          <div
            className="size-12 rounded-2xl flex items-center justify-center font-anton text-xl mb-3 shadow-lg"
            style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', color: 'var(--accent)' }}
          >
            SR.
          </div>

          <h3 className="text-xs font-semibold tracking-wider uppercase mb-1" style={{ color: 'var(--text-muted)' }}>
            Hey, I'm Satyajitsinh 👋
          </h3>
          <h2 className="font-anton text-3xl sm:text-5xl uppercase leading-tight mb-4" style={{ color: 'var(--text-primary)' }}>
            Project Coordinator <br />
            <span style={{ color: 'var(--accent)' }}>& CS Engineer</span>
          </h2>

          {/* 3D Memoji Avatar (Animated & Floating) */}
          <div className="relative size-28 sm:size-32 rounded-full p-1 bg-gradient-to-tr from-[var(--accent)] to-emerald-400 shadow-xl transition-transform hover:scale-105 duration-300 animate-float">
            <div className="size-full rounded-full overflow-hidden bg-white flex items-center justify-center">
              <img
                src="/images/avatar.png"
                alt="Satyajitsinh 3D Memoji Avatar"
                className="size-full object-cover"
              />
            </div>
          </div>
        </div>

        {/* Content Tabs / Q&A Area */}
        <div className="min-h-[220px] max-h-[360px] overflow-y-auto rounded-2xl p-4 mb-6 space-y-4" style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
          {activeTab === 'home' && (
            <div className="space-y-4 text-center sm:text-left py-2">
              <p className="text-base leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
                {portfolioData.personal.shortBio}
              </p>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
                {[
                  { label: 'Degree', val: 'B.Tech CSE (7.99 GPA)' },
                  { label: 'Exp', val: 'SHDPIXEL Coordinator' },
                  { label: 'Ad ROAS', val: '8× ROAS Campaign' },
                  { label: 'Location', val: 'Gujarat, India' },
                ].map(item => (
                  <div key={item.label} className="p-3 rounded-xl text-center" style={{ background: 'var(--bg-chip)', border: '1px solid var(--border)' }}>
                    <p className="text-[10px] uppercase tracking-wider font-semibold" style={{ color: 'var(--text-muted)' }}>{item.label}</p>
                    <p className="text-xs font-bold mt-1" style={{ color: 'var(--accent)' }}>{item.val}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'chat' && (
            <div className="space-y-3">
              {chatHistory.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[85%] rounded-2xl px-4 py-3 text-xs sm:text-sm whitespace-pre-line leading-relaxed ${
                      msg.sender === 'user'
                        ? 'font-medium text-white'
                        : 'font-normal'
                    }`}
                    style={msg.sender === 'user'
                      ? { background: 'var(--accent)', color: '#ffffff' }
                      : { background: 'var(--bg-chip)', color: 'var(--text-primary)', border: '1px solid var(--border)' }
                    }
                  >
                    {msg.text}
                  </div>
                </div>
              ))}
              <div ref={chatEndRef} />
            </div>
          )}

          {activeTab === 'projects' && (
            <div className="space-y-3">
              {portfolioData.projects.map(p => (
                <div key={p.id} className="p-3.5 rounded-xl flex items-center justify-between gap-4" style={{ background: 'var(--bg-chip)', border: '1px solid var(--border)' }}>
                  <div>
                    <p className="text-sm font-bold" style={{ color: 'var(--text-primary)' }}>{p.title}</p>
                    <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>{p.metrics}</p>
                  </div>
                  {p.link && p.link !== '#' && (
                    <a href={p.link} target="_blank" rel="noreferrer" className="p-2 rounded-lg bg-emerald-500/10 text-emerald-500 hover:bg-emerald-500/20">
                      <ExternalLink className="size-4" />
                    </a>
                  )}
                </div>
              ))}
            </div>
          )}

          {activeTab === 'skills' && (
            <div className="space-y-3">
              <div className="flex flex-wrap gap-2">
                {portfolioData.skillsList.map(s => (
                  <div key={s.id} className="px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5" style={{ background: 'var(--bg-chip)', border: '1px solid var(--border)' }}>
                    <span className="size-1.5 rounded-full" style={{ background: s.color }} />
                    <span style={{ color: 'var(--text-primary)' }}>{s.name}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'contact' && (
            <div className="space-y-3 text-center sm:text-left py-2">
              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>Ready to collaborate or discuss a project? Get in touch:</p>
              <div className="space-y-2 pt-2">
                <p className="text-sm font-bold" style={{ color: 'var(--accent)' }}>📧 {portfolioData.personal.email}</p>
                <p className="text-sm font-bold" style={{ color: 'var(--text-primary)' }}>📞 {portfolioData.personal.phone}</p>
                <p className="text-xs" style={{ color: 'var(--text-muted)' }}>📍 {portfolioData.personal.location}</p>
              </div>
            </div>
          )}
        </div>

        {/* Q&A Search Input */}
        <form onSubmit={handleSubmit} className="relative mb-6">
          <div
            className="flex items-center rounded-full py-2.5 px-4 transition-all border"
            style={{
              background: 'var(--bg-card)',
              borderColor: 'var(--border)',
            }}
          >
            <Search className="size-4 shrink-0 mr-3" style={{ color: 'var(--text-muted)' }} />
            <input
              type="text"
              placeholder="Ask me anything... (e.g. skills, projects, contact)"
              value={query}
              onChange={e => setQuery(e.target.value)}
              className="w-full bg-transparent text-sm outline-none"
              style={{ color: 'var(--text-primary)' }}
            />
            <button
              type="submit"
              disabled={!query.trim()}
              className="size-8 rounded-full flex items-center justify-center text-white transition-all disabled:opacity-40 shrink-0 ml-2"
              style={{ background: 'var(--accent)' }}
            >
              <ArrowRight className="size-4" />
            </button>
          </div>
        </form>

        {/* Quick Question Cards (aaabadcode style) */}
        <div className="grid grid-cols-5 gap-2">
          {[
            { id: 'home',     label: 'Me',        Icon: User,       q: 'Tell me about yourself' },
            { id: 'projects', label: 'Projects',  Icon: Briefcase,  q: 'Show top projects' },
            { id: 'skills',   label: 'Skills',    Icon: Layers,     q: 'What are your skills?' },
            { id: 'highlights', label: 'Fun',     Icon: Sparkles,   q: 'What is your background?' },
            { id: 'contact',  label: 'Contact',   Icon: PhoneCall,  q: 'How to contact you?' },
          ].map(({ id, label, Icon, q }) => (
            <button
              key={id}
              onClick={() => {
                setActiveTab(id);
                handleAsk(q);
              }}
              className="flex flex-col items-center justify-center p-3 rounded-2xl border transition-all duration-200 hover:scale-105 active:scale-95"
              style={activeTab === id
                ? { background: 'var(--accent-muted)', borderColor: 'var(--accent)', color: 'var(--accent)' }
                : { background: 'var(--bg-card)', borderColor: 'var(--border)', color: 'var(--text-secondary)' }
              }
            >
              <Icon className="size-4 mb-1" />
              <span className="text-[11px] font-semibold">{label}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
