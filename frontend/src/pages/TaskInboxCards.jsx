import React from 'react';

const TaskInboxCards = () => {
  return (
    <div className="bg-background-dark text-white font-display antialiased h-screen flex flex-col overflow-hidden selection:bg-primary selection:text-black">
      <div className="w-full h-12 flex items-center justify-between px-6 pt-2 z-50 shrink-0 bg-background-dark/80 backdrop-blur-md sticky top-0">
        <span className="text-sm font-medium opacity-80">9:41</span>
        <div className="flex items-center space-x-2 opacity-80">
          <span className="material-icons-round text-sm">
            signal_cellular_alt
          </span>
          <span className="material-icons-round text-sm">wifi</span>
          <span className="material-icons-round text-sm">battery_full</span>
        </div>
      </div>
      <header className="flex items-center justify-between px-6 py-3 border-b border-white/5 bg-background-dark/50 backdrop-blur-sm z-40">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-10 h-10 rounded-full bg-surface-dark flex items-center justify-center border border-white/10">
              <span className="material-icons-round text-primary text-xl">
                smart_toy
              </span>
            </div>
            <div className="absolute bottom-0 right-0 w-3 h-3 bg-primary rounded-full border-2 border-background-dark"></div>
          </div>
          <div>
            <h1 className="text-base font-bold text-white">Life Agent</h1>
            <p className="text-xs text-slate-400 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse"></span>
              Online
            </p>
          </div>
        </div>
        <button className="p-2 text-slate-400 hover:text-white transition-colors">
          <span className="material-icons-round">more_vert</span>
        </button>
      </header>
      <main className="flex-1 overflow-y-auto hide-scrollbar px-4 py-6 space-y-6">
        <div className="flex justify-center">
          <span className="px-3 py-1 bg-surface-dark rounded-full text-[10px] font-medium text-slate-400 uppercase tracking-wide border border-white/5">
            Today, 10:23 AM
          </span>
        </div>
        <div className="flex justify-end mb-2">
          <div className="bg-primary text-background-dark px-4 py-3 rounded-2xl rounded-tr-sm max-w-[80%] shadow-glow">
            <p className="text-sm font-medium">
              Show me my active fitness goal and catch me up on notifications.
            </p>
          </div>
        </div>
        <div className="flex justify-start items-end gap-2 mb-1">
          <div className="w-6 h-6 rounded-full bg-surface-dark flex items-center justify-center border border-white/10 shrink-0">
            <span className="material-icons-round text-primary text-[10px]">
              smart_toy
            </span>
          </div>
          <div className="bg-surface-dark border border-white/5 px-4 py-2 rounded-2xl rounded-tl-sm text-slate-300 text-sm">
            Sure, Alex. Here is your marathon training progress and a digest of
            your recent messages.
          </div>
        </div>
        <div className="flex justify-start pl-8 w-full max-w-md">
          <div className="w-full bg-surface-dark border border-white/10 rounded-2xl p-5 shadow-lg relative overflow-hidden group hover:border-primary/30 transition-colors">
            <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full blur-2xl -translate-y-1/2 translate-x-1/2 pointer-events-none"></div>
            <div className="flex justify-between items-start mb-4 relative z-10">
              <div className="flex gap-3 items-center">
                <div className="w-10 h-10 rounded-xl bg-orange-500/20 flex items-center justify-center text-orange-500 border border-orange-500/30">
                  <span className="material-symbols-outlined">
                    directions_run
                  </span>
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">
                    Marathon Training
                  </h3>
                  <p className="text-xs text-slate-400">
                    Week 4 of 16 • Long Run Phase
                  </p>
                </div>
              </div>
              <span className="bg-orange-500/20 text-orange-400 text-[10px] font-bold px-2 py-1 rounded-full uppercase tracking-wider border border-orange-500/20">
                Active Task
              </span>
            </div>
            <div className="mb-5 relative z-10">
              <div className="flex justify-between text-xs mb-2">
                <span className="text-slate-400">Weekly Goal</span>
                <span className="text-white font-bold">32 / 45 km</span>
              </div>
              <div className="w-full h-2 bg-black/40 rounded-full overflow-hidden border border-white/5">
                <div
                  className="h-full bg-gradient-to-r from-orange-500 to-amber-400 w-[71%] rounded-full shadow-[0_0_10px_rgba(249,115,22,0.5)]"
                ></div>
              </div>
              <p className="mt-2 text-xs text-slate-400">
                Next up: <span className="text-white font-medium">10km Tempo Run</span>
              </p>
            </div>
            <div className="flex gap-2 relative z-10">
              <button className="flex-1 bg-primary text-background-dark font-bold py-2.5 px-4 rounded-xl text-sm shadow-glow hover:bg-primary/90 hover:scale-[1.02] active:scale-95 transition-all flex items-center justify-center gap-2">
                <span className="material-icons-round text-lg">add_circle</span>
                Log Workout
              </button>
              <button className="w-10 flex items-center justify-center bg-white/5 text-white rounded-xl border border-white/10 hover:bg-white/10 transition-colors">
                <span className="material-icons-round">more_horiz</span>
              </button>
            </div>
          </div>
        </div>
        <div className="flex justify-start pl-8 w-full max-w-md pb-4">
          <div className="w-full bg-surface-dark border border-white/10 rounded-2xl overflow-hidden shadow-lg">
            <div className="bg-white/5 p-4 border-b border-white/5 flex justify-between items-center">
              <div className="flex items-center gap-2">
                <span className="material-icons-round text-primary text-sm">
                  mark_email_unread
                </span>
                <h3 className="text-sm font-bold text-white uppercase tracking-wide">
                  Message Digest
                </h3>
              </div>
              <span className="text-[10px] bg-white/10 px-2 py-0.5 rounded text-slate-300">
                Last 2 hours
              </span>
            </div>
            <div className="divide-y divide-white/5">
              <div className="p-4 hover:bg-white/5 transition-colors cursor-pointer group">
                <div className="flex items-start gap-3">
                  <div className="relative shrink-0">
                    <div className="w-8 h-8 rounded-lg bg-[#4A154B] flex items-center justify-center shrink-0">
                      <img
                        alt="Slack"
                        className="w-5 h-5"
                        src="https://lh3.googleusercontent.com/aida-public/AB6AXuAgZZr1ROQM1ftZYygU51oOdr4v2OBoD_15n8qKJGgRP5hIcvHGZhv03jF5ijDg6mVWqaWNIEO3dqDpfY8fC6rjWA6qf0Hhqqg6cS6ESv-9yqqXhvHobecWMmHc6qCSOrW6AGjwf-u-Pzcj1fwjSPn89sTfDukyIghkZLlfIC8xfEb8_fL9eZ_q6qD8meEFbGnNzm4QJ5ONdL29VWmADo8CD4g4gBgV7TaQmWtIGL5tSW5vIrXIgE7Y1CWO0QVChSuewq_vHGdAmTtA"
                      />
                    </div>
                    <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full border-2 border-surface-dark"></div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex justify-between items-baseline mb-0.5">
                      <h4 className="text-sm font-semibold text-white truncate">
                        Product Design
                      </h4>
                      <span className="text-[10px] text-slate-500">12m ago</span>
                    </div>
                    <p className="text-xs text-slate-400 line-clamp-2">
                      <span className="text-white font-medium">Sarah:</span> The
                      new mockups for the dashboard are ready for review. Can
                      everyone take a look before...
                    </p>
                  </div>
                  <span className="material-icons-round text-slate-600 group-hover:text-primary transition-colors text-sm self-center">
                    arrow_forward_ios
                  </span>
                </div>
              </div>
              <div className="p-4 hover:bg-white/5 transition-colors cursor-pointer group">
                <div className="flex items-start gap-3">
                  <div className="relative shrink-0">
                    <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center shrink-0 text-white font-bold text-xs">
                      G
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex justify-between items-baseline mb-0.5">
                      <h4 className="text-sm font-semibold text-white truncate">
                        Gmail - Updates
                      </h4>
                      <span className="text-[10px] text-slate-500">45m ago</span>
                    </div>
                    <p className="text-xs text-slate-400 line-clamp-1">
                      3 new newsletters from TechCrunch, The Verge...
                    </p>
                  </div>
                  <span className="material-icons-round text-slate-600 group-hover:text-primary transition-colors text-sm self-center">
                    arrow_forward_ios
                  </span>
                </div>
              </div>
            </div>
            <button className="w-full py-3 text-xs font-medium text-primary hover:bg-primary/5 transition-colors border-t border-white/5 flex items-center justify-center gap-1">
              View all notifications
              <span className="material-icons-round text-sm">expand_more</span>
            </button>
          </div>
        </div>
        <div className="h-16"></div>
      </main>
      <div className="absolute bottom-0 w-full bg-background-dark/95 backdrop-blur-xl border-t border-white/10 px-4 py-4 z-50">
        <div className="flex items-end gap-2 max-w-3xl mx-auto">
          <button className="p-3 rounded-full bg-white/5 text-slate-400 hover:text-primary hover:bg-white/10 transition-colors shrink-0">
            <span className="material-icons-round">add</span>
          </button>
          <div className="flex-1 bg-surface-dark border border-white/10 rounded-2xl flex items-center px-4 py-2 focus-within:border-primary/50 transition-colors shadow-inner">
            <input
              className="bg-transparent border-none text-white placeholder-slate-500 focus:ring-0 w-full text-sm py-2"
              placeholder="Type a message..."
              type="text"
            />
            <button className="text-slate-400 hover:text-white transition-colors ml-2">
              <span className="material-icons-round">mic</span>
            </button>
          </div>
          <button className="p-3 rounded-full bg-primary text-background-dark hover:bg-primary/90 transition-colors shrink-0 shadow-glow">
            <span className="material-icons-round">arrow_upward</span>
          </button>
        </div>
        <div className="h-5"></div>
      </div>
    </div>
  );
};

export default TaskInboxCards;
