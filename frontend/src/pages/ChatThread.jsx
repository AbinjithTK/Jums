import React from 'react';

const ChatThread = () => {
  return (
    <div className="bg-background-light dark:bg-background-dark font-display antialiased h-screen overflow-hidden flex flex-col text-slate-900 dark:text-white">
      {/* Top App Bar */}
      <header className="flex-none pt-12 pb-2 px-4 bg-background-light dark:bg-background-dark/95 backdrop-blur-md sticky top-0 z-50 border-b border-surface-highlight/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div
                className="size-10 rounded-full bg-cover bg-center ring-2 ring-surface-highlight"
                data-alt="Abstract minimalist 3D avatar of an AI assistant, glowing green and blue"
                style={{
                  backgroundImage: "url('https://lh3.googleusercontent.com/aida-public/AB6AXuBRt2XpRmf4EoYe-3Tf9rljWFRMLw6ADzjJ05Gn7jSccFad-LYSGgEBnaQVGPrN0jfqXN2wPnruSXiH0twLgK-dKBnlaL7PDa5Pr3gTLkWb6_HbRabKT7h9IVtcCX-AIcdrPsZ08g7fQmrqOl8fjebqOE75NLAJjb-Ku-luKac-gviyY4vKPzDYMNSVtYZtTo_SJmQGL2WIXEtdzsq8RE5VDHAHJmsi2z9xu5JTXGA-gMHfPSihn--34MXdrvl21p5aB8jZ0gy4gsVX')",
                }}
              ></div>
              <div className="absolute bottom-0 right-0 size-3 rounded-full bg-primary border-2 border-background-dark"></div>
            </div>
            <div>
              <h1 className="text-base font-bold leading-tight">Nova Assistant</h1>
              <p className="text-xs text-primary/80 font-medium">
                Active • Proactive Mode
              </p>
            </div>
          </div>
          <button className="size-10 flex items-center justify-center rounded-full hover:bg-surface-highlight text-slate-400 hover:text-white transition-colors">
            <span className="material-symbols-outlined">more_vert</span>
          </button>
        </div>
      </header>
      {/* Chat Thread (Scrollable Area) */}
      <main className="flex-1 overflow-y-auto p-4 space-y-6 scroll-smooth">
        {/* Date Divider */}
        <div className="flex items-center justify-center py-2">
          <span className="text-xs font-medium text-slate-500 bg-surface-dark px-3 py-1 rounded-full uppercase tracking-wider">
            Today, 9:00 AM
          </span>
        </div>
        {/* AI Message: Daily Briefing Card */}
        <div className="flex flex-col items-start gap-2 max-w-sm sm:max-w-md w-full">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold text-primary">NOVA</span>
            <span className="text-[10px] text-slate-500">09:01 AM</span>
          </div>
          {/* Daily Briefing Widget */}
          <div className="w-full bg-surface-dark rounded-2xl border border-surface-highlight overflow-hidden shadow-lg">
            {/* Header with Weather */}
            <div className="p-4 flex items-center justify-between bg-surface-highlight/30 border-b border-surface-highlight/50">
              <h3 className="font-bold text-lg">Daily Briefing</h3>
              <div className="flex items-center gap-2 text-sm">
                <span className="material-symbols-outlined text-yellow-400 text-[20px]">
                  sunny
                </span>
                <span>72°F</span>
              </div>
            </div>
            {/* Progress Section */}
            <div className="p-5 flex items-center gap-5">
              {/* Radial Progress (CSS Conic Gradient) */}
              <div
                className="relative size-16 shrink-0 rounded-full flex items-center justify-center bg-surface-highlight"
                style={{
                  background: "conic-gradient(#13ec5b 65%, #203324 0)",
                }}
              >
                <div className="absolute inset-1 bg-surface-dark rounded-full flex items-center justify-center">
                  <span className="text-xs font-bold text-white">65%</span>
                </div>
              </div>
              <div>
                <p className="text-sm font-semibold text-white">Goal Progress</p>
                <p className="text-xs text-slate-400 mt-1">
                  You're on track to hit your weekly targets. Keep it up!
                </p>
              </div>
            </div>
            {/* Plan List */}
            <div className="px-4 pb-4 space-y-2">
              <p className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
                Plan for Today
              </p>
              <label className="group flex items-start gap-3 p-2 rounded-lg hover:bg-surface-highlight/50 transition-colors cursor-pointer">
                <div className="relative flex items-center">
                  <input
                    className="peer size-5 appearance-none rounded border-2 border-slate-600 checked:bg-primary checked:border-primary transition-colors focus:ring-0 focus:ring-offset-0 focus:outline-none bg-transparent"
                    type="checkbox"
                  />
                  <span className="absolute inset-0 hidden peer-checked:flex items-center justify-center text-background-dark pointer-events-none">
                    <span className="material-symbols-outlined text-[16px] font-bold">
                      check
                    </span>
                  </span>
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-white group-hover:text-primary transition-colors peer-checked:line-through peer-checked:text-slate-500">
                    Review Q3 Report
                  </p>
                  <p className="text-xs text-slate-500">9:30 AM • Work</p>
                </div>
              </label>
              <label className="group flex items-start gap-3 p-2 rounded-lg hover:bg-surface-highlight/50 transition-colors cursor-pointer">
                <div className="relative flex items-center">
                  <input
                    className="peer size-5 appearance-none rounded border-2 border-slate-600 checked:bg-primary checked:border-primary transition-colors focus:ring-0 focus:ring-offset-0 focus:outline-none bg-transparent"
                    type="checkbox"
                  />
                  <span className="absolute inset-0 hidden peer-checked:flex items-center justify-center text-background-dark pointer-events-none">
                    <span className="material-symbols-outlined text-[16px] font-bold">
                      check
                    </span>
                  </span>
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-white group-hover:text-primary transition-colors peer-checked:line-through peer-checked:text-slate-500">
                    Call Mom
                  </p>
                  <p className="text-xs text-slate-500">12:00 PM • Personal</p>
                </div>
              </label>
            </div>
          </div>
        </div>
        {/* AI Message: Inbox Digest */}
        <div className="flex flex-col items-start gap-2 max-w-sm sm:max-w-md w-full">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold text-primary">NOVA</span>
            <span className="text-[10px] text-slate-500">10:45 AM</span>
          </div>
          <div className="w-full bg-surface-dark rounded-2xl border border-surface-highlight overflow-hidden shadow-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-bold text-sm flex items-center gap-2">
                <span className="material-symbols-outlined text-primary text-lg">
                  inbox
                </span>
                Inbox Digest
              </h4>
              <span className="text-xs bg-surface-highlight text-primary px-2 py-0.5 rounded">
                4 New
              </span>
            </div>
            <div className="space-y-3">
              {/* Message Item 1 */}
              <div className="flex gap-3 items-start">
                <div className="size-8 rounded-full bg-green-900/40 flex items-center justify-center text-green-400 shrink-0">
                  <span className="material-symbols-outlined text-[18px]">
                    chat
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex justify-between items-baseline">
                    <p className="text-sm font-medium text-white truncate">
                      Anna (WhatsApp)
                    </p>
                    <span className="text-[10px] text-slate-500">10m</span>
                  </div>
                  <p className="text-xs text-slate-400 truncate">
                    Are we still on for dinner tonight?
                  </p>
                </div>
              </div>
              {/* Message Item 2 */}
              <div className="flex gap-3 items-start">
                <div className="size-8 rounded-full bg-purple-900/40 flex items-center justify-center text-purple-400 shrink-0">
                  <span className="material-symbols-outlined text-[18px]">
                    tag
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex justify-between items-baseline">
                    <p className="text-sm font-medium text-white truncate">
                      Design Team (Slack)
                    </p>
                    <span className="text-[10px] text-slate-500">32m</span>
                  </div>
                  <p className="text-xs text-slate-400 truncate">
                    The final assets are ready for review.
                  </p>
                </div>
              </div>
              {/* Combined others */}
              <div className="flex gap-3 items-center pt-1">
                <div className="size-8 flex items-center justify-center shrink-0">
                  {/* spacer */}
                </div>
                <p className="text-xs text-slate-500 italic">
                  + 2 other messages from WhatsApp
                </p>
              </div>
            </div>
            <div className="mt-4 flex gap-2">
              <button className="flex-1 bg-surface-highlight hover:bg-surface-highlight/80 text-white text-xs font-semibold py-2 px-3 rounded-lg flex items-center justify-center gap-1 transition-colors">
                Expand All
                <span className="material-symbols-outlined text-[16px]">
                  expand_more
                </span>
              </button>
              <button className="flex-1 bg-primary/20 hover:bg-primary/30 text-primary text-xs font-semibold py-2 px-3 rounded-lg flex items-center justify-center gap-1 transition-colors">
                Quick Reply
                <span className="material-symbols-outlined text-[16px]">
                  bolt
                </span>
              </button>
            </div>
          </div>
        </div>
        {/* AI Message: Proactive Suggestion */}
        <div className="flex flex-col items-start gap-2 max-w-sm sm:max-w-md w-full">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold text-primary">NOVA</span>
            <span className="text-[10px] text-slate-500">Just now</span>
          </div>
          <div className="w-full relative group">
            {/* Glowing effect behind the card */}
            <div className="absolute -inset-0.5 bg-gradient-to-r from-primary/30 to-blue-500/30 rounded-2xl blur opacity-30 group-hover:opacity-50 transition duration-500"></div>
            <div className="relative bg-surface-dark rounded-2xl p-4 border border-primary/20">
              <div className="flex gap-3">
                <div className="shrink-0 size-10 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                  <span className="material-symbols-outlined">
                    directions_run
                  </span>
                </div>
                <div className="flex-1">
                  <p className="text-sm text-white leading-relaxed">
                    I see you're free at{' '}
                    <span className="text-primary font-bold">5 PM</span>. Should
                    we slot in that 5km run for your Marathon goal?
                  </p>
                </div>
              </div>
              <div className="mt-4 flex gap-2">
                <button className="bg-primary hover:bg-green-400 text-background-dark font-bold text-sm py-2 px-4 rounded-lg flex-1 transition-colors shadow-lg shadow-primary/20">
                  Confirm Run
                </button>
                <button className="bg-surface-highlight hover:bg-surface-highlight/80 text-white font-medium text-sm py-2 px-4 rounded-lg flex-1 transition-colors">
                  Reschedule
                </button>
              </div>
            </div>
          </div>
        </div>
        {/* Spacer for bottom composer */}
        <div className="h-20"></div>
      </main>
      {/* Bottom Composer Bar */}
      <footer className="flex-none p-4 pb-8 bg-background-light dark:bg-background-dark/95 backdrop-blur-md border-t border-surface-highlight/50 fixed bottom-0 left-0 right-0 z-50">
        <div className="max-w-3xl mx-auto flex items-end gap-3">
          <button className="shrink-0 size-10 rounded-full bg-surface-highlight hover:bg-surface-highlight/80 text-slate-400 hover:text-white flex items-center justify-center transition-colors">
            <span className="material-symbols-outlined">settings</span>
          </button>
          <div className="flex-1 bg-surface-dark border border-surface-highlight rounded-2xl flex items-center p-1.5 focus-within:border-primary/50 focus-within:ring-1 focus-within:ring-primary/20 transition-all shadow-sm">
            <input
              className="w-full bg-transparent border-none text-white placeholder-slate-500 focus:ring-0 text-sm px-3 py-2 h-10"
              placeholder="Ask anything or update tasks..."
              type="text"
            />
            <button className="size-9 rounded-xl bg-primary hover:bg-green-400 text-background-dark flex items-center justify-center transition-colors shadow-lg shadow-primary/20">
              <span className="material-symbols-outlined">mic</span>
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default ChatThread;
