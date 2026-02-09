import React from 'react';

const MemorySearch = () => {
  return (
    <div className="bg-black font-display antialiased h-screen w-full overflow-hidden flex flex-col justify-end relative">
      {/* Mock background representing the chat layer underneath */}
      <div
        className="absolute inset-0 z-0 bg-cover bg-center opacity-40 blur-sm scale-105"
        data-alt="Blurred abstract chat interface background"
        style={{
          backgroundImage:
            "url('https://lh3.googleusercontent.com/aida-public/AB6AXuBZhJNYqtTKWEFKg1Yy045-xT5t4jHKlb4z9dgTmn1en4hJAk-WcLG8iB96JXo-54RodOwiCdCIRwRWNeXbla0xSedVFiaoirF9YI9nrhMzxbJzp6a9QHhhWATh3ojPRjOSzd7i6gg6yd-C907NE5iY71m2CPo91FVEI8l7KNTCgiDkNN8GsNiK0ogWfSquXx4lHnF31De1ttzIINUc1LPIBuMxb11waOREpveNRJ3jlpoqFtqwWs8jMvsFn3EQPKzBjIzQf9eyuN-d')",
        }}
      ></div>
      <div className="absolute inset-0 z-0 bg-black/60"></div>
      {/* Main Slide-over Container */}
      <div className="relative z-10 w-full h-[92vh] flex flex-col bg-background-light dark:bg-background-dark rounded-t-3xl shadow-[0_-10px_40px_rgba(0,0,0,0.5)] overflow-hidden transition-transform duration-300 ease-out">
        {/* Drag Handle Area */}
        <div className="w-full flex justify-center pt-3 pb-2 flex-shrink-0 cursor-grab active:cursor-grabbing">
          <div className="h-1.5 w-12 rounded-full bg-gray-300 dark:bg-white/20"></div>
        </div>
        {/* Header: Title & Search */}
        <div className="px-5 pt-2 pb-4 flex flex-col gap-4 flex-shrink-0">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white tracking-tight">
            Memory Search
          </h1>
          {/* Search Input */}
          <div className="relative group">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <span className="material-symbols-outlined text-gray-400 group-focus-within:text-primary transition-colors duration-200">
                search
              </span>
            </div>
            <input
              autoFocus
              className="block w-full pl-10 pr-3 py-3.5 border-none rounded-xl bg-gray-100 dark:bg-surface-dark text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all text-base shadow-sm"
              placeholder="Search memories, goals, or messages..."
              type="text"
            />
            {/* Voice Input Icon (Optional visual detail) */}
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center cursor-pointer">
              <span className="material-symbols-outlined text-gray-400 hover:text-white transition-colors">
                mic
              </span>
            </div>
          </div>
          {/* Filter Pills */}
          <div className="flex gap-3 overflow-x-auto no-scrollbar pb-1">
            <button className="flex items-center gap-1.5 px-4 py-2 rounded-full bg-primary text-black font-medium text-sm whitespace-nowrap shadow-md shadow-primary/20 transition-transform active:scale-95">
              <span className="material-symbols-outlined text-[18px]">
                grid_view
              </span>
              All
            </button>
            <button className="flex items-center gap-1.5 px-4 py-2 rounded-full bg-gray-200 dark:bg-surface-dark text-gray-600 dark:text-gray-300 font-medium text-sm border border-transparent dark:border-white/5 hover:bg-gray-300 dark:hover:bg-white/10 whitespace-nowrap transition-colors active:scale-95">
              <span className="material-symbols-outlined text-[18px]">
                style
              </span>
              Cards
            </button>
            <button className="flex items-center gap-1.5 px-4 py-2 rounded-full bg-gray-200 dark:bg-surface-dark text-gray-600 dark:text-gray-300 font-medium text-sm border border-transparent dark:border-white/5 hover:bg-gray-300 dark:hover:bg-white/10 whitespace-nowrap transition-colors active:scale-95">
              <span className="material-symbols-outlined text-[18px]">
                chat_bubble
              </span>
              Messages
            </button>
            <button className="flex items-center gap-1.5 px-4 py-2 rounded-full bg-gray-200 dark:bg-surface-dark text-gray-600 dark:text-gray-300 font-medium text-sm border border-transparent dark:border-white/5 hover:bg-gray-300 dark:hover:bg-white/10 whitespace-nowrap transition-colors active:scale-95">
              <span className="material-symbols-outlined text-[18px]">
                photo_library
              </span>
              Photos
            </button>
            <button className="flex items-center gap-1.5 px-4 py-2 rounded-full bg-gray-200 dark:bg-surface-dark text-gray-600 dark:text-gray-300 font-medium text-sm border border-transparent dark:border-white/5 hover:bg-gray-300 dark:hover:bg-white/10 whitespace-nowrap transition-colors active:scale-95">
              <span className="material-symbols-outlined text-[18px]">
                flag
              </span>
              Goals
            </button>
          </div>
        </div>
        {/* Scrollable Content Area */}
        <div className="flex-1 overflow-y-auto px-5 pb-8 space-y-6">
          {/* Recent Results Section */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400">
                Top Matches
              </h3>
              <button className="text-xs text-primary font-medium hover:text-primary/80">
                Clear History
              </button>
            </div>
            <div className="space-y-3">
              {/* Result Item: Card (Trip) */}
              <div className="group flex flex-col gap-2 p-4 rounded-xl bg-white dark:bg-surface-dark border border-gray-100 dark:border-white/5 active:bg-gray-50 dark:active:bg-white/5 transition-colors cursor-pointer shadow-sm">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="flex items-center justify-center w-6 h-6 rounded bg-purple-500/20 text-purple-400">
                      <span className="material-symbols-outlined text-[16px]">
                        flight_takeoff
                      </span>
                    </span>
                    <span className="text-xs font-medium text-gray-500 dark:text-gray-400">
                      Oct 12, 2023
                    </span>
                  </div>
                  <span className="material-symbols-outlined text-gray-400 text-[18px]">
                    chevron_right
                  </span>
                </div>
                <div className="flex gap-3">
                  <div className="w-16 h-16 rounded-lg bg-gray-200 dark:bg-gray-700 flex-shrink-0 overflow-hidden relative">
                    <img
                      className="w-full h-full object-cover"
                      data-alt="Tokyo city street view at night neon lights"
                      data-location="Tokyo, Japan"
                      src="https://lh3.googleusercontent.com/aida-public/AB6AXuATA6ssCKBx94x7BCMUQbkYt5zlLHPmWhCu-OtG3QQMxmHx7_m15hu80cWntfBsmxkBeDDfstfX-qOtbshCxg8VGG_vhoXQM51LyycN_agu1DymCpgxylBL54jSckSBfk4PljkhnOBxHlIKjjTVXZwsHUD3MgOA3PRGzlJIr9BsZnvE_V1R55Yy_Jev2MHglNvqxSEIfKXK-iUadW2x6BeHS5KnZRn0Y6hoeTo27xHxD_PkBwMvYYIxxGZoDK-52DwSvH2WlMuYmJKa"
                    />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="text-base font-semibold text-gray-900 dark:text-white truncate">
                      Tokyo Trip Itinerary
                    </h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2 leading-relaxed">
                      Flight{' '}
                      <span className="text-primary font-medium">JL405</span>{' '}
                      departs at 10:30 AM from Haneda. Hotel reservation
                      confirmed at Shinjuku Granbell.
                    </p>
                  </div>
                </div>
              </div>
              {/* Result Item: Goal (Run) */}
              <div className="group flex flex-col gap-2 p-4 rounded-xl bg-white dark:bg-surface-dark border border-gray-100 dark:border-white/5 active:bg-gray-50 dark:active:bg-white/5 transition-colors cursor-pointer shadow-sm">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="flex items-center justify-center w-6 h-6 rounded bg-orange-500/20 text-orange-400">
                      <span className="material-symbols-outlined text-[16px]">
                        fitness_center
                      </span>
                    </span>
                    <span className="text-xs font-medium text-gray-500 dark:text-gray-400">
                      Yesterday
                    </span>
                  </div>
                  <span className="material-symbols-outlined text-gray-400 text-[18px]">
                    chevron_right
                  </span>
                </div>
                <div>
                  <h4 className="text-base font-semibold text-gray-900 dark:text-white mb-1">
                    Morning 5km Run
                  </h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                    Completed in{' '}
                    <span className="text-white bg-primary/20 px-1 rounded text-xs font-mono">
                      24:30
                    </span>
                    . Heart rate avg 145bpm. Felt strong on the last kilometer.
                  </p>
                </div>
              </div>
              {/* Result Item: Message (Grocery) */}
              <div className="group flex flex-col gap-2 p-4 rounded-xl bg-white dark:bg-surface-dark border border-gray-100 dark:border-white/5 active:bg-gray-50 dark:active:bg-white/5 transition-colors cursor-pointer shadow-sm">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="flex items-center justify-center w-6 h-6 rounded bg-blue-500/20 text-blue-400">
                      <span className="material-symbols-outlined text-[16px]">
                        chat
                      </span>
                    </span>
                    <span className="text-xs font-medium text-gray-500 dark:text-gray-400">
                      Sept 05, 2023
                    </span>
                  </div>
                  <span className="material-symbols-outlined text-gray-400 text-[18px]">
                    chevron_right
                  </span>
                </div>
                <div>
                  <h4 className="text-base font-semibold text-gray-900 dark:text-white mb-1">
                    Grocery List Reminder
                  </h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                    Don't forget to pick up milk, eggs, sourdough bread, and
                    fresh spinach for the salad.
                  </p>
                </div>
              </div>
            </div>
          </div>
          {/* Past Month Section */}
          <div className="pt-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-3">
              Past Month
            </h3>
            <div className="space-y-3">
              {/* Result Item: Photo Memory */}
              <div className="group flex flex-row gap-4 p-3 rounded-xl hover:bg-gray-100 dark:hover:bg-white/5 transition-colors cursor-pointer items-center border border-transparent hover:border-gray-200 dark:hover:border-white/5">
                <div className="w-12 h-12 rounded-lg bg-gray-700 overflow-hidden flex-shrink-0 relative">
                  <img
                    className="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity"
                    data-alt="Portrait of a woman looking thoughtful"
                    src="https://lh3.googleusercontent.com/aida-public/AB6AXuBKJCwaeTLqMFG11Tw7BqHPw7GQ1d_MuuOFZ7NvuqAbRcvbRGJKxJlv3YGoHV9HacwKpoPIC-SXCYy_wLKF07l0m1cAfbZpnT6Cm5OQZpCM-bUhMG-exkr_Na58SQGAh5MviuE8c70QYmk6bJqEYbGTfJlYBt03nTzYvnwhGcyvzFJjUOwdOF_Lxw9aT9A61qUc7Pe6z0QuEyb_0AyjHAZDc6MYpiPq1JQ_sMa4vvqgcgEoeIFOqNGwYa8HXPsbz_-rbDhbUrs7tpmA"
                  />
                </div>
                <div className="flex-1 min-w-0 border-b border-gray-100 dark:border-white/5 pb-3 group-hover:border-transparent">
                  <div className="flex justify-between items-baseline">
                    <h4 className="text-sm font-semibold text-gray-900 dark:text-white truncate">
                      Portrait Session
                    </h4>
                    <span className="text-xs text-gray-500 dark:text-gray-500">
                      Aug 28
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                    Added 14 new photos to "Summer Portfolio" album.
                  </p>
                </div>
              </div>
              {/* Result Item: Document/Card */}
              <div className="group flex flex-row gap-4 p-3 rounded-xl hover:bg-gray-100 dark:hover:bg-white/5 transition-colors cursor-pointer items-center border border-transparent hover:border-gray-200 dark:hover:border-white/5">
                <div className="w-12 h-12 rounded-lg bg-indigo-500/20 flex items-center justify-center flex-shrink-0 text-indigo-400">
                  <span className="material-symbols-outlined">description</span>
                </div>
                <div className="flex-1 min-w-0 border-b border-gray-100 dark:border-white/5 pb-3 group-hover:border-transparent">
                  <div className="flex justify-between items-baseline">
                    <h4 className="text-sm font-semibold text-gray-900 dark:text-white truncate">
                      Project Alpha Specs
                    </h4>
                    <span className="text-xs text-gray-500 dark:text-gray-500">
                      Aug 20
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                    Updated requirements for the Q4 launch phase.
                  </p>
                </div>
              </div>
            </div>
          </div>
          {/* Bottom Spacer for better scrolling on mobile */}
          <div className="h-8"></div>
        </div>
      </div>
    </div>
  );
};

export default MemorySearch;
