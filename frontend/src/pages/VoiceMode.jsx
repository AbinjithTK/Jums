import React from 'react';

const VoiceMode = () => {
  return (
    <div className="bg-deep-green text-white font-display antialiased h-screen flex flex-col overflow-hidden relative selection:bg-primary selection:text-black">
      <div className="absolute top-0 w-full h-12 flex items-center justify-between px-6 pt-2 z-50 shrink-0">
        <span className="text-sm font-medium opacity-80">9:41</span>
        <div className="flex items-center space-x-2 opacity-80">
          <span className="material-symbols-outlined text-[18px]">
            signal_cellular_alt
          </span>
          <span className="material-symbols-outlined text-[18px]">wifi</span>
          <span className="material-symbols-outlined text-[18px]">
            battery_full
          </span>
        </div>
      </div>
      <div className="absolute inset-0 bg-gradient-to-b from-background-dark via-deep-green to-black pointer-events-none"></div>
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-96 h-96 bg-primary/10 rounded-full blur-[100px] pointer-events-none"></div>
      <button className="absolute top-14 right-6 z-40 w-10 h-10 flex items-center justify-center rounded-full bg-surface-dark/50 backdrop-blur-md text-white/70 hover:bg-surface-dark hover:text-white transition-colors">
        <span className="material-symbols-outlined">close</span>
      </button>
      <main className="relative z-10 flex flex-col items-center justify-between h-full px-8 pb-12 pt-32 w-full max-w-md mx-auto">
        <div className="w-full text-center space-y-6">
          <h1 className="text-4xl md:text-5xl font-bold leading-tight tracking-tight text-white drop-shadow-lg">
            I've rescheduled your sync.{' '}
            <span className="text-primary">Anything else?</span>
          </h1>
        </div>
        <div className="flex-1 flex items-center justify-center relative w-full">
          <div className="absolute w-64 h-64 bg-primary/20 rounded-full blur-3xl animate-pulse-slow"></div>
          <div className="absolute w-48 h-48 bg-primary/30 rounded-full blur-2xl animate-pulse"></div>
          <div className="relative w-32 h-32 rounded-full bg-gradient-to-br from-primary to-green-600 orb-shadow flex items-center justify-center animate-orb-breathe z-20">
            <div className="absolute inset-0 rounded-full bg-white/20 blur-sm"></div>
            <span className="material-symbols-outlined text-4xl text-white drop-shadow-md">
              graphic_eq
            </span>
          </div>
          <div className="absolute w-56 h-56 border border-primary/20 rounded-full animate-[spin_10s_linear_infinite]">
            <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 w-2 h-2 bg-primary rounded-full shadow-[0_0_10px_#13ec5b]"></div>
          </div>
          <div className="absolute w-72 h-72 border border-white/5 rounded-full animate-[spin_15s_linear_infinite_reverse]">
            <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2 w-1.5 h-1.5 bg-white/50 rounded-full"></div>
          </div>
        </div>
        <div className="w-full flex flex-col items-center gap-8 mb-8">
          <div className="h-16 flex items-center justify-center gap-1.5 w-full max-w-[280px]">
            <div className="waveform-bar h-4 delay-[0ms]"></div>
            <div className="waveform-bar h-8 delay-[100ms]"></div>
            <div className="waveform-bar h-5 delay-[50ms]"></div>
            <div className="waveform-bar h-10 delay-[200ms]"></div>
            <div className="waveform-bar h-6 delay-[150ms]"></div>
            <div className="waveform-bar h-12 delay-[300ms]"></div>
            <div className="waveform-bar h-8 delay-[75ms]"></div>
            <div className="waveform-bar h-14 delay-[250ms]"></div>
            <div className="waveform-bar h-7 delay-[125ms]"></div>
            <div className="waveform-bar h-10 delay-[225ms]"></div>
            <div className="waveform-bar h-4 delay-[25ms]"></div>
            <div className="waveform-bar h-8 delay-[175ms]"></div>
            <div className="waveform-bar h-5 delay-[60ms]"></div>
          </div>
          <div className="flex items-center gap-6">
            <button className="w-14 h-14 rounded-full bg-surface-dark border border-white/10 flex items-center justify-center text-white hover:bg-white/10 transition-colors">
              <span className="material-symbols-outlined">keyboard</span>
            </button>
            <button className="w-20 h-20 rounded-full bg-white text-black flex items-center justify-center shadow-[0_0_20px_rgba(255,255,255,0.3)] hover:scale-105 transition-transform">
              <span className="material-symbols-outlined text-4xl">
                mic_off
              </span>
            </button>
            <button className="w-14 h-14 rounded-full bg-surface-dark border border-white/10 flex items-center justify-center text-white hover:bg-white/10 transition-colors">
              <span className="material-symbols-outlined">more_horiz</span>
            </button>
          </div>
          <p className="text-white/40 text-sm font-medium">Tap to interrupt</p>
        </div>
      </main>
      <style>{`
        .orb-shadow {
            box-shadow: 0 0 100px 30px rgba(19, 236, 91, 0.2);
        }
      `}</style>
    </div>
  );
};

export default VoiceMode;
