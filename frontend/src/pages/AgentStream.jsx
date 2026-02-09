import React from 'react';

const AgentStream = () => {
  return (
    <div className="bg-background-light dark:bg-background-dark font-display text-slate-900 dark:text-white antialiased h-screen w-full flex flex-col overflow-hidden">
      {/* Header */}
      <header className="flex items-center justify-between p-4 pt-12 pb-2 bg-background-light dark:bg-background-dark sticky top-0 z-20">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div
              className="size-10 rounded-full bg-cover bg-center border border-white/10 shadow-sm"
              data-alt="AI Agent Avatar"
              style={{
                backgroundImage:
                  "url('https://lh3.googleusercontent.com/aida-public/AB6AXuDZw5uUXtv7cvoEOrmycM-rIb1T8vcjX-HaMu5EYbjnouadw0WAYzlqdO50ULDjQXfglh7KEXP-0y4bNiA0Bu-vB_6W_1PM2iz4FTbI6KX6LnKCClkrWMSDhRPnJi87xfI9PwFn4BEK_enjFeKqz_lH7X_UMc8XrcDB0wEQdBBvGpZ-04jijKPs1KcjyRNMEMGLMGCznonA-gWH6kcbBPVS_j3L51NK52yvAYjH2oBNA_KRuXvJqyE7TtLx8oec5d161uif7X3axB4E')",
              }}
            ></div>
            <div className="absolute bottom-0 right-0 size-2.5 bg-primary rounded-full border-2 border-background-dark thinking-dot"></div>
          </div>
          <div>
            <h1 className="text-base font-bold leading-tight tracking-tight dark:text-white">
              Afternoon Update
            </h1>
            <p className="text-xs text-slate-500 dark:text-emerald-400/70 font-medium">
              Assistant Active
            </p>
          </div>
        </div>
        <button className="text-slate-500 dark:text-white/60 hover:text-primary transition-colors">
          <span className="material-symbols-outlined">more_vert</span>
        </button>
      </header>
      {/* Main Stream Area */}
      <main className="flex-1 overflow-y-auto px-4 pb-24 flex flex-col gap-6 scroll-smooth">
        {/* Timestamp */}
        <div className="w-full text-center py-2">
          <span className="text-xs font-medium text-slate-400 dark:text-emerald-500/50 bg-slate-100 dark:bg-white/5 px-3 py-1 rounded-full">
            Today, 4:20 PM
          </span>
        </div>
        {/* Card 1: Goal Check-in (Completed/Informational State) */}
        <div className="w-full max-w-md mx-auto bg-white dark:bg-surface-card rounded-2xl overflow-hidden shadow-sm border border-slate-100 dark:border-white/5">
          {/* Card Image Header */}
          <div className="relative h-32 w-full">
            <div
              className="absolute inset-0 bg-cover bg-center"
              data-alt="Runner stretching legs on a track at sunset"
              style={{
                backgroundImage:
                  "url('https://lh3.googleusercontent.com/aida-public/AB6AXuDz8Lp_CR93G22R0wOr-8Pq6BFaL8AS6TkqwAd1Bs47xdEEzwA8HR8Ej_31Sq_TrNOhX1rZ6KrgCcoyyEMe7xJFT7PXDOXwoW0wzoRxf8EKd2-KdSQyydWuXsGLj75GayU0qk_znjOo1wGkl_aWlnMV8qz3_hWylPYk5zWj-4O-BJ0uJA9m-nboYT2Lz61m6Gv9Ul9I6vqnh6rnbSMyZtNEd5lFL01MjrAtN8bLtTMMRFjYXxRhAO_M_XIjvNk2tjeyx6oOEBSLQaQG')",
              }}
            ></div>
            <div className="absolute inset-0 bg-gradient-to-t from-surface-card via-surface-card/60 to-transparent"></div>
            <div className="absolute bottom-3 left-4 right-4 flex justify-between items-end">
              <div>
                <div className="flex items-center gap-1.5 mb-1">
                  <span className="material-symbols-outlined text-primary text-sm">
                    fitness_center
                  </span>
                  <span className="text-xs font-bold text-primary uppercase tracking-wider">
                    Goal Check-in
                  </span>
                </div>
                <h3 className="text-white text-lg font-bold leading-tight">
                  Run a Half Marathon
                </h3>
              </div>
            </div>
          </div>
          <div className="p-4 pt-2">
            <p className="text-slate-500 dark:text-slate-300 text-sm mb-4">
              You're on a streak! 3 days in a row.
            </p>
            {/* Progress Block */}
            <div className="bg-slate-50 dark:bg-black/20 rounded-xl p-3 mb-4">
              <div className="flex justify-between items-end mb-2">
                <span className="text-xs font-semibold dark:text-white">
                  Weekly Distance
                </span>
                <span className="text-xs font-bold text-primary">15/21 km</span>
              </div>
              <div className="relative h-2 w-full bg-slate-200 dark:bg-white/10 rounded-full overflow-hidden">
                <div
                  className="absolute top-0 left-0 h-full bg-primary rounded-full"
                  style={{ width: '71%' }}
                ></div>
              </div>
            </div>
            <button className="w-full flex items-center justify-center gap-2 bg-primary hover:bg-emerald-400 text-background-dark font-bold text-sm py-3 px-4 rounded-xl transition-all active:scale-[0.98]">
              <span className="material-symbols-outlined text-[18px]">
                add_circle
              </span>
              Log today's run
            </button>
          </div>
        </div>
        {/* Card 2: Unified Reply (Active State) */}
        <div className="w-full max-w-md mx-auto relative group">
          {/* Active Indicator Glow */}
          <div className="absolute -inset-0.5 bg-gradient-to-b from-primary/30 to-transparent rounded-[18px] blur opacity-40 group-hover:opacity-60 transition duration-500"></div>
          <div className="relative bg-white dark:bg-[#152019] rounded-2xl p-4 border border-primary/20 shadow-lg">
            {/* Header */}
            <div className="flex items-center justify-between mb-3 pb-3 border-b border-slate-100 dark:border-white/5">
              <div className="flex items-center gap-2">
                <div className="size-6 bg-[#25D366] rounded-full flex items-center justify-center text-white">
                  <svg
                    className="size-3.5"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.008-.57-.008-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"></path>
                  </svg>
                </div>
                <span className="text-sm font-bold text-slate-800 dark:text-slate-100">
                  Mom
                </span>
                <span className="text-xs text-slate-400 dark:text-slate-500">
                  • WhatsApp
                </span>
              </div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-primary bg-primary/10 px-2 py-0.5 rounded">
                Action Required
              </span>
            </div>
            {/* Message Content */}
            <div className="bg-slate-50 dark:bg-black/20 rounded-lg p-3 mb-4 rounded-tl-none border-l-2 border-primary/50">
              <p className="text-sm dark:text-slate-200 leading-relaxed">
                Hey! Are we still on for 7pm? Dad is asking if we should pick up
                dessert.
              </p>
            </div>
            {/* AI Chips */}
            <div className="flex flex-wrap gap-2">
              <button className="flex-1 min-w-[100px] bg-slate-100 dark:bg-surface-dark hover:bg-primary/20 dark:hover:bg-primary/20 border border-transparent hover:border-primary/50 transition-all rounded-full px-4 py-2 text-xs font-medium dark:text-white text-center">
                Running late
              </button>
              <button className="flex-1 min-w-[100px] bg-primary text-background-dark font-bold hover:brightness-110 transition-all rounded-full px-4 py-2 text-xs text-center shadow-[0_0_10px_rgba(19,236,91,0.2)]">
                On my way!
              </button>
              <button className="flex-1 min-w-[100px] bg-slate-100 dark:bg-surface-dark hover:bg-primary/20 dark:hover:bg-primary/20 border border-transparent hover:border-primary/50 transition-all rounded-full px-4 py-2 text-xs font-medium dark:text-white text-center">
                Yes, 7pm works
              </button>
            </div>
          </div>
        </div>
        {/* Spacer for scrolling */}
        <div className="h-4"></div>
      </main>
      {/* Bottom Composer Area */}
      <div className="w-full bg-background-light dark:bg-background-dark/95 backdrop-blur-md border-t border-slate-200 dark:border-white/5 p-4 pb-8 z-30">
        {/* AI Thinking/Context Indicator */}
        <div className="flex items-center gap-2 mb-3 px-1">
          <div className="flex gap-1">
            <div className="size-1.5 bg-primary rounded-full animate-[bounce_1s_infinite_0ms]"></div>
            <div className="size-1.5 bg-primary rounded-full animate-[bounce_1s_infinite_200ms]"></div>
            <div className="size-1.5 bg-primary rounded-full animate-[bounce_1s_infinite_400ms]"></div>
          </div>
          <span className="text-xs font-medium text-primary uppercase tracking-wider">
            Agent is ready
          </span>
        </div>
        <div className="flex items-end gap-3">
          <button className="size-12 shrink-0 rounded-full bg-slate-200 dark:bg-surface-card text-slate-500 dark:text-slate-400 flex items-center justify-center hover:bg-slate-300 dark:hover:bg-white/10 transition-colors">
            <span className="material-symbols-outlined">add</span>
          </button>
          <div className="flex-1 bg-white dark:bg-surface-card rounded-[24px] min-h-[48px] flex items-center px-4 border border-transparent focus-within:border-primary/50 transition-all shadow-sm">
            <input
              className="w-full bg-transparent border-none text-sm dark:text-white placeholder-slate-400 focus:ring-0 p-0 leading-normal"
              placeholder="Type a message or command..."
              type="text"
            />
          </div>
          <button className="size-12 shrink-0 rounded-full bg-primary text-background-dark flex items-center justify-center hover:brightness-110 transition-all shadow-[0_0_15px_rgba(19,236,91,0.3)]">
            <span className="material-symbols-outlined filled">mic</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default AgentStream;
