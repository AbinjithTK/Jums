import React from 'react';

const MvpConfig = () => {
  return (
    <div className="bg-background-light dark:bg-background-dark text-slate-800 dark:text-white font-display antialiased h-screen flex flex-col overflow-hidden selection:bg-primary selection:text-black">
      <div className="absolute inset-0 z-0 flex flex-col opacity-30 filter blur-sm pointer-events-none">
        <div className="w-full h-12 flex items-center justify-between px-6 pt-2 shrink-0">
          <span className="text-sm font-medium opacity-80">9:41</span>
          <div className="flex items-center space-x-2 opacity-80">
            <span className="material-icons-round text-sm">
              signal_cellular_alt
            </span>
            <span className="material-icons-round text-sm">wifi</span>
            <span className="material-icons-round text-sm">battery_full</span>
          </div>
        </div>
        <main className="flex-1 overflow-y-auto hide-scrollbar px-4 pb-24 pt-4 space-y-4">
          <div className="flex items-start max-w-[85%]">
            <div className="w-8 h-8 rounded-full bg-primary/20 border border-primary/50 flex items-center justify-center mr-2 flex-shrink-0">
              <span className="material-icons-round text-primary text-sm">
                smart_toy
              </span>
            </div>
            <div className="bg-white dark:bg-surface-dark border border-slate-200 dark:border-white/10 rounded-2xl rounded-tl-none p-3 shadow-sm">
              <p className="text-sm text-slate-800 dark:text-slate-200">
                I've connected to your calendar. Would you like me to review
                your schedule for conflicts?
              </p>
            </div>
          </div>
          <div className="flex items-start justify-end max-w-[85%] ml-auto">
            <div className="bg-primary text-background-dark rounded-2xl rounded-tr-none p-3 shadow-glow">
              <p className="text-sm font-medium">Yes, please check next week.</p>
            </div>
          </div>
          <div className="flex items-start max-w-[85%]">
            <div className="w-8 h-8 rounded-full bg-primary/20 border border-primary/50 flex items-center justify-center mr-2 flex-shrink-0">
              <span className="material-icons-round text-primary text-sm">
                smart_toy
              </span>
            </div>
            <div className="bg-white dark:bg-surface-dark border border-slate-200 dark:border-white/10 rounded-2xl rounded-tl-none p-3 shadow-sm">
              <p className="text-sm text-slate-800 dark:text-slate-200">
                Checking... found 2 overlapping meetings on Tuesday.
              </p>
            </div>
          </div>
        </main>
      </div>
      <div className="absolute inset-0 bg-black/40 z-10 backdrop-blur-sm"></div>
      <div className="absolute bottom-0 left-0 right-0 z-20 bg-white dark:bg-[#16291d] rounded-t-[32px] shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        <div className="w-full flex justify-center pt-3 pb-2 shrink-0">
          <div className="w-12 h-1.5 bg-slate-200 dark:bg-white/20 rounded-full"></div>
        </div>
        <div className="px-6 pb-4 flex justify-between items-center shrink-0 border-b border-slate-100 dark:border-white/5">
          <div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">
              Agent Settings
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Customize your AI assistant's brain
            </p>
          </div>
          <button className="w-8 h-8 rounded-full bg-slate-100 dark:bg-surface-dark flex items-center justify-center text-slate-500 hover:bg-slate-200 dark:hover:bg-white/10 transition-colors">
            <span className="material-icons-round text-lg">close</span>
          </button>
        </div>
        <div className="flex-1 overflow-y-auto hide-scrollbar p-6 space-y-8">
          <section>
            <label className="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-3 block">
              Inference Model
            </label>
            <div className="relative group">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <span className="material-icons-round text-primary text-xl">
                  psychology
                </span>
              </div>
              <select className="block w-full pl-10 pr-10 py-3.5 text-sm bg-slate-50 dark:bg-surface-dark border border-slate-200 dark:border-white/10 rounded-xl focus:ring-primary focus:border-primary text-slate-900 dark:text-white appearance-none cursor-pointer hover:bg-slate-100 dark:hover:bg-surface-dark/80 transition-colors">
                <option value="neural-v2">Neural-v2 (Reasoning)</option>
                <option value="neural-v1">Neural-v1 (Fast)</option>
                <option value="legacy">Legacy-3.5</option>
              </select>
              <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                <span className="material-icons-round text-slate-400">
                  expand_more
                </span>
              </div>
            </div>
            <p className="mt-2 text-[10px] text-slate-400 dark:text-slate-500 px-1">
              Neural-v2 is recommended for complex planning tasks.
            </p>
          </section>
          <section>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-3">
              Connected Channels
            </h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-4 bg-slate-50 dark:bg-surface-dark border border-slate-200 dark:border-white/5 rounded-2xl">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 rounded-full bg-[#25D366]/10 flex items-center justify-center text-[#25D366]">
                    <span className="material-symbols-outlined text-2xl">
                      chat
                    </span>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-slate-900 dark:text-white">
                      WhatsApp
                    </p>
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      Daily summaries
                    </p>
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    defaultChecked
                    className="sr-only peer"
                    type="checkbox"
                  />
                  <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer dark:bg-slate-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary"></div>
                </label>
              </div>
              <div className="flex items-center justify-between p-4 bg-slate-50 dark:bg-surface-dark border border-slate-200 dark:border-white/5 rounded-2xl">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 rounded-full bg-[#E01E5A]/10 flex items-center justify-center text-[#E01E5A]">
                    <span className="material-symbols-outlined text-2xl">
                      work
                    </span>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-slate-900 dark:text-white">
                      Slack
                    </p>
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      Work updates
                    </p>
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    className="sr-only peer"
                    type="checkbox"
                  />
                  <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer dark:bg-slate-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary"></div>
                </label>
              </div>
            </div>
          </section>
          <section>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-3">
              Active Skills
            </h3>
            <div className="flex items-center justify-between p-4 bg-slate-50 dark:bg-surface-dark border border-slate-200 dark:border-white/5 rounded-2xl">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-full bg-blue-500/10 flex items-center justify-center text-blue-500">
                  <span className="material-icons-round text-xl">
                    event_available
                  </span>
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-900 dark:text-white">
                    Calendar Sync
                  </p>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    Read & Write access
                  </p>
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  defaultChecked
                  className="sr-only peer"
                  type="checkbox"
                />
                <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer dark:bg-slate-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary"></div>
              </label>
            </div>
          </section>
          <section className="pt-2">
            <div className="p-4 rounded-2xl border border-red-100 dark:border-red-900/30 bg-red-50/50 dark:bg-red-900/10 flex flex-col gap-3">
              <div className="flex items-start gap-3">
                <span className="material-icons-round text-red-500 mt-0.5">
                  delete_history
                </span>
                <div>
                  <h4 className="text-sm font-bold text-red-600 dark:text-red-400">
                    Reset Memory
                  </h4>
                  <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                    This will wipe all context learned from previous
                    conversations. This action cannot be undone.
                  </p>
                </div>
              </div>
              <button className="w-full mt-2 bg-white dark:bg-surface-dark border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 font-medium py-2.5 rounded-xl text-sm hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors">
                Reset Agent Memory
              </button>
            </div>
          </section>
          <div className="h-6"></div>
        </div>
      </div>
    </div>
  );
};

export default MvpConfig;
