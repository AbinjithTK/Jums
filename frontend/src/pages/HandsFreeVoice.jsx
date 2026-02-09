import React from 'react';

const HandsFreeVoice = () => {
  return (
    <div
      className="font-display antialiased h-screen overflow-hidden flex flex-col text-white relative"
      style={{
        background:
          'radial-gradient(circle at center, #102a1b 0%, #05110a 100%)',
      }}
    >
      <header className="flex-none pt-12 px-6 flex justify-between items-center z-50">
        <button className="size-10 flex items-center justify-center rounded-full bg-surface-highlight/40 hover:bg-surface-highlight/60 backdrop-blur-md transition-colors">
          <span className="material-symbols-outlined text-white/70">close</span>
        </button>
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-surface-highlight/30 backdrop-blur-md border border-white/5">
          <div className="size-2 rounded-full bg-red-500 animate-pulse"></div>
          <span className="text-xs font-medium text-white/70 tracking-wide uppercase">
            Listening
          </span>
        </div>
        <button className="size-10 flex items-center justify-center rounded-full bg-surface-highlight/40 hover:bg-surface-highlight/60 backdrop-blur-md transition-colors">
          <span className="material-symbols-outlined text-white/70">mic</span>
        </button>
      </header>
      <main className="flex-1 flex flex-col items-center justify-center relative px-6 z-10">
        <div className="text-center mb-12 max-w-sm mx-auto">
          <p className="text-2xl md:text-3xl font-semibold leading-tight text-white/90 drop-shadow-lg">
            "Nova, what's my next meeting?"
          </p>
        </div>
        <div className="relative size-48 md:size-64 flex items-center justify-center mb-12">
          <div className="absolute inset-0 bg-primary/20 rounded-full blur-3xl opacity-30 animate-pulse-slow"></div>
          <div className="absolute inset-4 bg-primary/30 rounded-full blur-2xl opacity-40"></div>
          <div className="relative size-32 md:size-40 rounded-full bg-gradient-to-tr from-primary/10 to-emerald-400/20 backdrop-blur-sm border border-primary/30 flex items-center justify-center orb-pulse">
            <div
              className="absolute inset-0 rounded-full bg-primary/10 animate-ping opacity-20"
              style={{ animationDuration: '3s' }}
            ></div>
            <div className="size-24 rounded-full bg-gradient-to-b from-primary/20 to-transparent flex items-center justify-center">
              <span className="material-symbols-outlined text-primary/80 text-5xl">
                graphic_eq
              </span>
            </div>
          </div>
        </div>
        <div className="text-center max-w-md mx-auto opacity-0 animate-[fadeIn_0.5s_ease-out_forwards_0.5s]">
          <div className="inline-flex items-center gap-2 mb-2">
            <span className="size-1.5 rounded-full bg-primary"></span>
            <span className="text-xs font-bold tracking-widest text-primary uppercase">
              Nova
            </span>
          </div>
          <p className="text-lg md:text-xl font-medium text-emerald-100/80 leading-relaxed">
            "Your next meeting is a Strategy Sync at 2:00 PM."
          </p>
        </div>
      </main>
      <div className="h-32 w-full flex items-end justify-center gap-1.5 pb-12 px-4 opacity-60">
        <div className="waveform-bar h-10"></div>
        <div className="waveform-bar h-14"></div>
        <div className="waveform-bar h-8"></div>
        <div className="waveform-bar h-20"></div>
        <div className="waveform-bar h-12"></div>
        <div className="waveform-bar h-24"></div>
        <div className="waveform-bar h-16"></div>
        <div className="waveform-bar h-10"></div>
        <div className="waveform-bar h-28"></div>
        <div className="waveform-bar h-14"></div>
        <div className="waveform-bar h-6"></div>
        <div className="waveform-bar h-18"></div>
        <div className="waveform-bar h-12"></div>
        <div className="waveform-bar h-20"></div>
        <div className="waveform-bar h-8"></div>
        <div className="waveform-bar h-14"></div>
        <div className="waveform-bar h-10"></div>
      </div>
      <div className="absolute top-1/4 left-0 w-72 h-72 bg-emerald-900/20 rounded-full mix-blend-screen filter blur-3xl opacity-30 animate-blob"></div>
      <div className="absolute bottom-1/4 right-0 w-72 h-72 bg-primary/10 rounded-full mix-blend-screen filter blur-3xl opacity-30 animate-blob animation-delay-2000"></div>
      <style>{`
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .animation-delay-2000 {
            animation-delay: 2s;
        }
      `}</style>
    </div>
  );
};

export default HandsFreeVoice;
