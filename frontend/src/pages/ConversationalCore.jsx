import React from 'react';

const ConversationalCore = () => {
  return (
    <div className="bg-background-light dark:bg-background-dark text-slate-800 dark:text-white font-display antialiased flex flex-col overflow-hidden selection:bg-primary selection:text-black h-screen">
      <div className="w-full h-12 flex items-center justify-between px-6 pt-2 z-50 shrink-0 bg-background-light/90 dark:bg-background-dark/90 backdrop-blur-sm fixed top-0 left-0 right-0">
        <span className="text-sm font-medium opacity-80">9:41</span>
        <div className="flex items-center space-x-2 opacity-80">
          <span className="material-icons-round text-sm">
            signal_cellular_alt
          </span>
          <span className="material-icons-round text-sm">wifi</span>
          <span className="material-icons-round text-sm">battery_full</span>
        </div>
      </div>
      <main className="flex-1 overflow-y-auto hide-scrollbar px-4 pt-20 pb-24 w-full max-w-lg mx-auto">
        <div className="flex flex-col space-y-2 mb-8 animate-[fadeIn_0.5s_ease-out]">
          <div className="flex items-end space-x-2">
            <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center shrink-0 shadow-glow">
              <span className="material-icons-round text-background-dark text-lg">
                smart_toy
              </span>
            </div>
            <div className="bg-white dark:bg-chat-bubble-dark p-4 rounded-2xl rounded-bl-none shadow-sm border border-slate-100 dark:border-white/5 max-w-[85%]">
              <p className="text-sm text-slate-700 dark:text-slate-200 leading-relaxed">
                Hi Alex! I've set up your dashboard. Here is your briefing for
                the day and a few channels to connect to get started.
              </p>
            </div>
          </div>
        </div>
        <div className="flex flex-col space-y-2 mb-6 pl-10 animate-[fadeIn_0.6s_ease-out_0.2s_both]">
          <div className="bg-white dark:bg-surface-dark border border-slate-200 dark:border-white/10 rounded-2xl p-5 shadow-lg w-full">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">
                Daily Briefing
              </h3>
              <span className="text-xs text-slate-400">Today</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex flex-col">
                <div className="flex items-center space-x-2 mb-1">
                  <span className="text-3xl">⛅</span>
                  <span className="text-3xl font-bold text-slate-900 dark:text-white">
                    72°
                  </span>
                </div>
                <span className="text-sm text-slate-500 dark:text-slate-400">
                  Partly Cloudy • High 76°
                </span>
              </div>
              <div className="relative w-16 h-16 flex items-center justify-center">
                <svg className="w-full h-full transform -rotate-90">
                  <circle
                    className="text-slate-100 dark:text-white/10"
                    cx="32"
                    cy="32"
                    fill="transparent"
                    r="28"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <circle
                    className="text-primary opacity-30"
                    cx="32"
                    cy="32"
                    fill="transparent"
                    r="28"
                    stroke="currentColor"
                    strokeDasharray="175"
                    strokeDashoffset="175"
                    strokeLinecap="round"
                    strokeWidth="4"
                  ></circle>
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-xs font-bold text-slate-400">0%</span>
                </div>
              </div>
            </div>
            <div className="mt-4 pt-4 border-t border-slate-100 dark:border-white/5">
              <p className="text-sm text-slate-600 dark:text-slate-300 italic">
                "Every journey begins with a single step. Let's set a goal."
              </p>
            </div>
          </div>
        </div>
        <div className="flex flex-col space-y-2 mb-6 pl-10 animate-[fadeIn_0.7s_ease-out_0.4s_both]">
          <div className="bg-white dark:bg-surface-dark border border-slate-200 dark:border-white/10 rounded-2xl p-5 shadow-lg w-full">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-4">
              Connect Channels
            </h3>
            <div className="space-y-3">
              <button className="w-full flex items-center justify-between bg-slate-50 dark:bg-white/5 hover:bg-slate-100 dark:hover:bg-white/10 border border-slate-200 dark:border-white/5 p-3 rounded-xl transition-colors group">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 rounded-full bg-[#25D366]/20 flex items-center justify-center">
                    <svg
                      className="w-4 h-4 text-[#25D366] fill-current"
                      viewBox="0 0 24 24"
                    >
                      <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"></path>
                    </svg>
                  </div>
                  <span className="font-medium text-slate-800 dark:text-white">
                    WhatsApp
                  </span>
                </div>
                <span className="text-xs font-bold text-primary bg-primary/10 px-3 py-1.5 rounded-full group-hover:bg-primary group-hover:text-background-dark transition-colors">
                  Connect
                </span>
              </button>
              <button className="w-full flex items-center justify-between bg-slate-50 dark:bg-white/5 hover:bg-slate-100 dark:hover:bg-white/10 border border-slate-200 dark:border-white/5 p-3 rounded-xl transition-colors group">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 rounded-full bg-[#4A154B]/20 flex items-center justify-center">
                    <svg
                      className="w-4 h-4 text-[#4A154B] dark:text-[#E01E5A] fill-current"
                      viewBox="0 0 24 24"
                    >
                      <path d="M5.042 15.165a2.528 2.528 0 0 1-2.52 2.523A2.528 2.528 0 0 1 0 15.165a2.527 2.527 0 0 1 2.522-2.52h2.52v2.52zM6.313 15.165a2.527 2.527 0 0 1 2.521-2.52 2.527 2.527 0 0 1 2.521 2.52v6.313A2.528 2.528 0 0 1 8.834 24a2.528 2.528 0 0 1-2.521-2.524v-6.31zM8.834 5.042a2.528 2.528 0 0 1-2.521-2.52A2.528 2.528 0 0 1 8.834 0a2.528 2.528 0 0 1 2.521 2.522v2.52h-2.52zM8.834 6.313a2.528 2.528 0 0 1 2.521 2.521 2.528 2.528 0 0 1-2.521 2.521H2.522A2.528 2.528 0 0 1 0 8.834a2.528 2.528 0 0 1 2.522-2.521h6.312zM18.956 8.834a2.528 2.528 0 0 1 2.522-2.521A2.528 2.528 0 0 1 24 8.834a2.528 2.528 0 0 1-2.522 2.521h-2.52v-2.52zM17.688 8.834a2.528 2.528 0 0 1-2.522 2.521 2.527 2.527 0 0 1-2.52-2.521V2.522A2.527 2.527 0 0 1 15.166 0a2.528 2.528 0 0 1 2.522 2.522v6.312zM15.166 18.956a2.528 2.528 0 0 1 2.522 2.522A2.528 2.528 0 0 1 15.166 24a2.527 2.527 0 0 1-2.522-2.522v-2.52h2.52zM15.166 17.688a2.527 2.527 0 0 1-2.522-2.522 2.527 2.527 0 0 1 2.522-2.52h6.312A2.527 2.527 0 0 1 24 15.166a2.528 2.528 0 0 1-2.522 2.522h-6.312z"></path>
                    </svg>
                  </div>
                  <span className="font-medium text-slate-800 dark:text-white">
                    Slack
                  </span>
                </div>
                <span className="text-xs font-bold text-primary bg-primary/10 px-3 py-1.5 rounded-full group-hover:bg-primary group-hover:text-background-dark transition-colors">
                  Connect
                </span>
              </button>
            </div>
          </div>
        </div>
      </main>
      <footer className="fixed bottom-0 w-full bg-white dark:bg-background-dark/95 backdrop-blur-lg border-t border-slate-200 dark:border-white/5 z-20 pb-6 pt-3 px-4">
        <div className="max-w-lg mx-auto flex items-center gap-3">
          <button className="w-10 h-10 rounded-full bg-slate-100 dark:bg-white/5 flex items-center justify-center text-slate-400 hover:text-slate-600 dark:hover:text-white transition-colors">
            <span className="material-icons-round text-xl">settings</span>
          </button>
          <div className="flex-1 relative">
            <input
              className="w-full bg-slate-100 dark:bg-surface-dark border-transparent focus:border-primary/50 focus:ring-0 rounded-full py-3 px-5 text-sm text-slate-800 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 shadow-inner"
              placeholder="Message..."
              type="text"
            />
          </div>
          <button className="w-12 h-12 rounded-full bg-primary text-background-dark shadow-glow flex items-center justify-center transform active:scale-95 transition-all">
            <span className="material-icons-round text-2xl">mic</span>
          </button>
        </div>
      </footer>
      <div className="fixed top-0 left-0 w-full h-64 bg-primary/5 dark:bg-primary/5 blur-3xl rounded-full -translate-y-1/2 pointer-events-none z-0"></div>
    </div>
  );
};

export default ConversationalCore;
