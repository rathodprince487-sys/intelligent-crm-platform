import React, { useState } from 'react';
import { portfolioData } from '../data/portfolioData';
import { Mail, Phone, MapPin, Send, Check, Copy } from 'lucide-react';
import { GithubIcon, LinkedinIcon } from './Icons';

export const Contact = () => {
  const [formData, setFormData] = useState({ name: '', email: '', subject: '', message: '' });
  const [submitted, setSubmitted] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.name || !formData.email || !formData.message) return;
    setSubmitted(true);
    setTimeout(() => {
      setSubmitted(false);
      setFormData({ name: '', email: '', subject: '', message: '' });
    }, 4000);
  };

  const handleCopyEmail = () => {
    navigator.clipboard.writeText(portfolioData.personal.email);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  return (
    <section id="contact" className="py-28 relative" style={{ borderTop: '1px solid var(--border)' }}>
      <div className="max-w-7xl mx-auto px-6">
        {/* Header */}
        <div className="mb-16">
          <p className="text-xs uppercase tracking-widest mb-4" style={{ color: 'var(--text-muted)' }}>
            — Get in touch
          </p>
          <h2 className="font-anton text-5xl sm:text-8xl uppercase leading-none" style={{ color: 'var(--text-primary)' }}>
            Let's work<br />
            <span style={{ color: 'var(--accent)' }}>together</span>
          </h2>
        </div>

        <div className="grid lg:grid-cols-12 gap-16 items-start">
          {/* Left — contact info */}
          <div className="lg:col-span-5 space-y-10">
            <p className="text-base sm:text-lg font-light leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
              Open to full-time roles, freelance projects, and collaboration on automation or web development. Reach out — I usually reply within 24 hours.
            </p>

            {/* Contact details */}
            <div className="space-y-0">
              {[
                { Icon: Mail,   text: portfolioData.personal.email,    href: `mailto:${portfolioData.personal.email}`, color: 'var(--accent)' },
                { Icon: Phone,  text: portfolioData.personal.phone,    href: `tel:${portfolioData.personal.phone}`,    color: '#22d3ee' },
                { Icon: MapPin, text: portfolioData.personal.location, href: null,                                     color: '#a78bfa' },
              ].map(({ Icon, text, href, color }) => (
                <div key={text} className="flex items-center gap-4 py-5" style={{ borderBottom: '1px solid var(--border)' }}>
                  <Icon className="size-4 shrink-0" style={{ color }} />
                  {href ? (
                    <a href={href} className="text-sm font-medium hover:underline" style={{ color: 'var(--text-primary)' }}>{text}</a>
                  ) : (
                    <span className="text-sm" style={{ color: 'var(--text-primary)' }}>{text}</span>
                  )}
                  {href?.startsWith('mailto') && (
                    <button
                      onClick={handleCopyEmail}
                      className="ml-auto icon-btn px-3 py-1.5 rounded-lg text-[11px] font-bold flex items-center gap-1.5"
                    >
                      {copied ? <><Check className="size-3" /><span>Copied</span></> : <><Copy className="size-3" /><span>Copy</span></>}
                    </button>
                  )}
                </div>
              ))}
            </div>

            {/* Socials */}
            <div className="flex items-center gap-3">
              {[
                { href: portfolioData.personal.githubUrl,   Icon: GithubIcon,   label: 'GitHub' },
                { href: portfolioData.personal.linkedinUrl, Icon: LinkedinIcon, label: 'LinkedIn' },
              ].map(({ href, Icon, label }) => (
                <a
                  key={href}
                  href={href}
                  target="_blank"
                  rel="noreferrer"
                  className="icon-btn h-10 px-4 rounded-full flex items-center gap-2 text-xs font-semibold"
                >
                  <Icon className="size-3.5" />
                  <span>{label}</span>
                </a>
              ))}
            </div>
          </div>

          {/* Right — form */}
          <div className="lg:col-span-7">
            {submitted ? (
              <div className="py-20 text-center space-y-4">
                <div
                  className="size-16 rounded-full mx-auto flex items-center justify-center"
                  style={{ background: 'rgba(52,211,153,0.12)', border: '1px solid rgba(52,211,153,0.35)', color: '#34d399' }}
                >
                  <Check className="size-8" />
                </div>
                <h3 className="text-2xl font-syne font-bold" style={{ color: 'var(--text-primary)' }}>
                  Message sent!
                </h3>
                <p className="text-sm max-w-xs mx-auto" style={{ color: 'var(--text-secondary)' }}>
                  I'll get back to you as soon as possible.
                </p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-5">
                <div className="grid sm:grid-cols-2 gap-5">
                  {[
                    { label: 'Name',    key: 'name',    type: 'text',  ph: 'Your name' },
                    { label: 'Email',   key: 'email',   type: 'email', ph: 'your@email.com' },
                  ].map(({ label, key, type, ph }) => (
                    <div key={key}>
                      <label className="block text-xs font-semibold mb-2" style={{ color: 'var(--text-muted)' }}>{label}</label>
                      <input
                        type={type}
                        required
                        value={formData[key]}
                        onChange={e => setFormData({ ...formData, [key]: e.target.value })}
                        placeholder={ph}
                        className="form-input w-full px-4 py-3 rounded-xl text-sm"
                      />
                    </div>
                  ))}
                </div>

                <div>
                  <label className="block text-xs font-semibold mb-2" style={{ color: 'var(--text-muted)' }}>Subject</label>
                  <input
                    type="text"
                    value={formData.subject}
                    onChange={e => setFormData({ ...formData, subject: e.target.value })}
                    placeholder="Project inquiry / Job opportunity"
                    className="form-input w-full px-4 py-3 rounded-xl text-sm"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold mb-2" style={{ color: 'var(--text-muted)' }}>Message</label>
                  <textarea
                    rows={5}
                    required
                    value={formData.message}
                    onChange={e => setFormData({ ...formData, message: e.target.value })}
                    placeholder="Tell me about your project or role..."
                    className="form-input w-full px-4 py-3 rounded-xl text-sm resize-none"
                  />
                </div>

                <button
                  type="submit"
                  className="btn-primary w-full py-4 rounded-xl font-bold text-sm flex items-center justify-center gap-2"
                >
                  <span>Send Message</span>
                  <Send className="size-4" />
                </button>
              </form>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="mt-24 pt-8 flex justify-center text-xs" style={{ borderTop: '1px solid var(--border)', color: 'var(--text-muted)' }}>
          <p>© {new Date().getFullYear()} Satyajitsinh Rathod. All rights reserved.</p>
        </div>
      </div>
    </section>
  );
};
