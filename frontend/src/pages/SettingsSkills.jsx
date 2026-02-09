import React from 'react';

const SettingsSkills = () => {
  return (
    <div className="bg-black font-display antialiased overflow-hidden h-screen">
      {/* Background Simulation: Blurred Chat Interface behind the modal */}
      <div
        className="fixed inset-0 z-0 bg-cover bg-center opacity-40 blur-sm pointer-events-none"
        data-alt="Abstract dark gradient background representing chat interface"
        style={{
          backgroundImage:
            "url('https://lh3.googleusercontent.com/aida-public/AB6AXuAf9W3k_D1-PbDju2ZhXHvnv7uj10JrsiiCBsAEw1SelYQQJvrzndBBjwprh1YbkLryfX9XmpE-JV-Xax0-bI3CuTGE4nj7tzYASdS7w96erCCVPfRuzWLekqgJN_dsV81Nr6PfW7OgrDP1yoMxeSbL-0LO7FKB6mUfRKq2O-ASKF7POaR_zx1DEeupfgM16XpCRZa7xniCFhnbcmPAEjoWOkhxvEGW92myaSQhA_0gjtnmz2ejBlxRhfLlkeNLJtAobeVtcBHajzRw')",
        }}
      ></div>
      {/* Modal Backdrop */}
      <div className="fixed inset-0 z-10 bg-black/60 flex flex-col justify-end">
        {/* Bottom Sheet Container */}
        <div className="relative w-full max-w-md mx-auto bg-background-light dark:bg-[#111813] rounded-t-[2rem] shadow-2xl overflow-hidden flex flex-col h-[90vh] transition-transform duration-300 ease-out transform translate-y-0">
          {/* Drag Handle Area */}
          <div className="w-full flex justify-center pt-3 pb-2 bg-background-light dark:bg-[#111813] shrink-0 cursor-grab active:cursor-grabbing">
            <div className="h-1.5 w-12 rounded-full bg-gray-300 dark:bg-gray-600"></div>
          </div>
          {/* Header */}
          <div className="flex items-center justify-between px-6 pb-4 bg-background-light dark:bg-[#111813] shrink-0 border-b border-gray-200 dark:border-white/5">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white tracking-tight">
              Agent Configuration
            </h2>
            <button className="flex items-center justify-center w-8 h-8 rounded-full bg-gray-200 dark:bg-white/10 hover:bg-gray-300 dark:hover:bg-white/20 transition-colors">
              <span className="material-symbols-outlined text-gray-600 dark:text-gray-300 text-[20px]">
                close
              </span>
            </button>
          </div>
          {/* Scrollable Content */}
          <div className="flex-1 overflow-y-auto p-4 space-y-6 bg-gray-50 dark:bg-[#0c120e]">
            {/* SECTION: Connected Channels */}
            <div>
              <h3 className="px-2 mb-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Connected Channels
              </h3>
              <div className="bg-white dark:bg-[#1c2e22] rounded-2xl overflow-hidden shadow-sm border border-gray-100 dark:border-white/5">
                {/* WhatsApp */}
                <div className="flex items-center justify-between p-4 border-b border-gray-100 dark:border-white/5 group active:bg-gray-50 dark:active:bg-white/5 transition-colors">
                  <div className="flex items-center gap-4">
                    <div className="flex items-center justify-center w-10 h-10 rounded-full bg-[#25D366]/20 text-[#25D366]">
                      <span className="material-symbols-outlined">chat</span>{' '}
                      {/* Fallback icon since Whatsapp specific isn't in Material Symbols generic set, context implies app */}
                    </div>
                    <div>
                      <p className="text-base font-medium text-gray-900 dark:text-white">
                        WhatsApp
                      </p>
                      <p className="text-xs text-primary font-medium">
                        Active • Last msg 2m ago
                      </p>
                    </div>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      defaultChecked
                      className="sr-only peer"
                      type="checkbox"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                  </label>
                </div>
                {/* Slack */}
                <div className="flex items-center justify-between p-4 border-b border-gray-100 dark:border-white/5 group active:bg-gray-50 dark:active:bg-white/5 transition-colors">
                  <div className="flex items-center gap-4">
                    <div className="flex items-center justify-center w-10 h-10 rounded-full bg-[#4A154B]/20 text-[#E01E5A] dark:text-[#E01E5A]">
                      <span className="material-symbols-outlined">work</span>
                    </div>
                    <div>
                      <p className="text-base font-medium text-gray-900 dark:text-white">
                        Slack
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        Disconnected
                      </p>
                    </div>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      className="sr-only peer"
                      type="checkbox"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                  </label>
                </div>
                {/* Telegram */}
                <div className="flex items-center justify-between p-4 group active:bg-gray-50 dark:active:bg-white/5 transition-colors">
                  <div className="flex items-center gap-4">
                    <div className="flex items-center justify-center w-10 h-10 rounded-full bg-[#24A1DE]/20 text-[#24A1DE]">
                      <span className="material-symbols-outlined">send</span>
                    </div>
                    <div>
                      <p className="text-base font-medium text-gray-900 dark:text-white">
                        Telegram
                      </p>
                      <p className="text-xs text-primary font-medium">
                        Active • Syncing...
                      </p>
                    </div>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      defaultChecked
                      className="sr-only peer"
                      type="checkbox"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                  </label>
                </div>
              </div>
            </div>
            {/* SECTION: Skills */}
            <div>
              <h3 className="px-2 mb-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Active Skills
              </h3>
              <div className="bg-white dark:bg-[#1c2e22] rounded-2xl overflow-hidden shadow-sm border border-gray-100 dark:border-white/5">
                {/* Calendar Sync */}
                <button className="w-full flex items-center justify-between p-4 border-b border-gray-100 dark:border-white/5 hover:bg-gray-50 dark:hover:bg-white/5 transition-colors text-left">
                  <div className="flex items-center gap-4">
                    <div className="flex items-center justify-center w-10 h-10 rounded-full bg-orange-500/20 text-orange-500">
                      <span className="material-symbols-outlined">
                        calendar_month
                      </span>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <p className="text-base font-medium text-gray-900 dark:text-white">
                          Calendar Sync
                        </p>
                        <span className="material-symbols-outlined text-[14px] text-gray-400">
                          lock
                        </span>
                      </div>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        Read/Write Access
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-400">Config</span>
                    <span className="material-symbols-outlined text-gray-400">
                      chevron_right
                    </span>
                  </div>
                </button>
                {/* Health Connect */}
                <button className="w-full flex items-center justify-between p-4 hover:bg-gray-50 dark:hover:bg-white/5 transition-colors text-left">
                  <div className="flex items-center gap-4">
                    <div className="flex items-center justify-center w-10 h-10 rounded-full bg-red-500/20 text-red-500">
                      <span className="material-symbols-outlined">favorite</span>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <p className="text-base font-medium text-gray-900 dark:text-white">
                          Health Connect
                        </p>
                        <span className="material-symbols-outlined text-[14px] text-gray-400">
                          lock
                        </span>
                      </div>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        Steps & Sleep
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-primary">Auth</span>
                    <span className="material-symbols-outlined text-gray-400">
                      chevron_right
                    </span>
                  </div>
                </button>
              </div>
            </div>
            {/* SECTION: Gateway Configuration */}
            <div>
              <h3 className="px-2 mb-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Gateway Configuration
              </h3>
              <div className="bg-gradient-to-br from-[#1c2e22] to-[#142018] rounded-2xl p-5 border border-primary/20 shadow-lg relative overflow-hidden">
                {/* Decoration */}
                <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full blur-2xl -mr-10 -mt-10"></div>
                <div className="relative z-10 flex flex-col gap-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-xs text-primary font-bold tracking-widest uppercase mb-1">
                        Current Model
                      </p>
                      <h4 className="text-xl font-bold text-white">
                        Neural-v2 (Fast)
                      </h4>
                    </div>
                    <div className="px-2 py-1 rounded bg-primary/20 border border-primary/30">
                      <p className="text-[10px] font-bold text-primary uppercase">
                        Valid Key
                      </p>
                    </div>
                  </div>
                  <div className="h-px w-full bg-white/10 my-1"></div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-gray-400">
                      <span className="material-symbols-outlined text-[18px]">
                        speed
                      </span>
                      <span className="text-xs">Latency: 45ms</span>
                    </div>
                    <button className="text-xs font-semibold text-white bg-white/10 hover:bg-white/20 px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1">
                      Change Model
                      <span className="material-symbols-outlined text-[14px]">
                        expand_more
                      </span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
            {/* Danger Zone / Footer */}
            <div className="pt-4 pb-8 flex flex-col items-center gap-4">
              <button className="text-sm text-red-400 hover:text-red-300 transition-colors font-medium">
                Reset Agent Memory
              </button>
              <p className="text-[10px] text-gray-600 dark:text-gray-500 text-center">
                Version 2.4.0 • Build 8921
                <br />
                AI Life Assistant Inc.
              </p>
            </div>
          </div>
          {/* Bottom Fade for scrolling illusion */}
          <div className="absolute bottom-0 left-0 w-full h-8 bg-gradient-to-t from-background-light dark:from-[#0c120e] to-transparent pointer-events-none"></div>
        </div>
      </div>
    </div>
  );
};

export default SettingsSkills;
