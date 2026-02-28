---
title: "I Won Anthropic's Hackathon by Building a Band That Doesn't Wait for AI"
date: 2026-02-28
categories:
- Programming
summary: "How a Korg keyboard obsession and 1,134 lines of C led me to win the Creative Exploration of Opus 4.6 category in Anthropic's Built with Opus 4.6 hackathon."
---

I was watching the final round judging and winner announcement live on the Claude Discord. My wife was next to me playing PlayStation. Neither of us expected much. Then the host mentioned my name as the winner for Creative Exploration, and we both just froze. My project, Conductr, won the "Creative Exploration of Opus 4.6" category in Anthropic's "Built with Opus 4.6" hackathon. The prize was $5,000 in API credits. If you've ever built anything with large language models, you know is basically fuel for months of experimentation.

![Final judge](../../../public/blog-img/opus-final-judging.jpg)

Let me give you some context on the scale. Over 13,000 people applied to this hackathon. Anthropic selected 500 participants and gave each of us $500 in API credits to build something with Claude Opus 4.6. Out of those 500, 277 actually submitted projects, competing for a total prize pool of $100,000.

What struck me most wasn't my own win. It was the diversity of winners. The first place ($25,000) went to a lawyer. Third place went to a cardiologist. One of the "Keep Thinking" award winners was a road engineer. These weren't the usual suspects from Silicon Valley startups. The hackathon genuinely rewarded creative thinking from people who brought their own domain expertise to the table.

For me, that domain expertise was the intersection of two things I've been obsessed with for years: code and music. If you've been reading my blog, you know I've built [a voltage sequencer for my Eurorack system](making-sequencer-esp32.md), [experimented with programmable music](geekcamp-jakarta-2015-programmable-music.md), and spent way too many hours with my [Korg Kross 2 workstation](why-i-use-keyboard-workstation.md). Conductr came from all of that.

### The Keyboard That Planted the Seed

If you've ever played a Korg keyboard, specifically a KARMA-equipped one like the Korg Kronos or the original KARMA workstation, you've experienced something magical. KARMA stands for Kay Algorithmic Realtime Music Architecture. It's a system designed by Stephen Kay that generates musical patterns in real time based on algorithmic rules. Not pre-recorded loops. Not simple arpeggios. Actual procedural, rule-based MIDI generation with over 400 configurable parameters per effect.

You hold a chord, and KARMA produces a full musical arrangement around it: drum patterns, bass lines, melodic phrases, rhythmic comping. It responds to your playing dynamics, your note choices, and your timing. It feels alive.

The problem? KARMA is very complex. Those 400+ parameters per effect are powerful, but configuring them is like programming a synthesizer from the 1970s. It's deep, rewarding, and almost impossible for most musicians to figure out. I've never actually had the opportunity to play a KARMA-equipped keyboard myself, but I'm always amazed watching it in action from countless videos on YouTube. I've honestly wanted to buy myself the new Korg Kronos for a while now.

That's where the idea hit me. What if an AI handled the musical direction? Instead of manually tweaking hundreds of parameters, you just play and the AI listens, analyzes what you're doing, and adjusts the arrangement to complement your performance. That became Conductr. The tagline: "Play anything, Opus arranges the band."

### 1,134 Lines of C, Zero Heap Allocation

The heart of Conductr is a generative MIDI engine I call libgenseq. It's written in C. 1,134 lines, roughly 3.6KB of memory usage, and zero runtime heap allocation. Everything is statically allocated. Why C? Because I originally planned this as a hardware product running on a microcontroller, and in that world, you don't get the luxury of dynamic memory allocation.

The engine has four generators, each responsible for a different musical role:

1. **Drums**: uses Euclidean rhythms to spread hits evenly across a pattern. If you haven't heard of Euclidean rhythms, they're a mathematical way to space N hits across M steps as evenly as possible. It turns out most traditional drum patterns from around the world are Euclidean.
2. **Bass**: template-based with scale awareness. It follows the root note and chord tones, applying rhythmic templates that give it a human feel.
3. **Melody**: constrained random walk. It moves step by step through the scale with occasional leaps, staying within a configurable range. Think of it as a wandering musician who knows the key signature.
4. **Harmony**: diatonic interval offsets from the melody. It creates chord voicings that move in parallel with the melodic line.

All four generators share a musical context: root note, scale (stored as a 12-bit bitmask, one bit per semitone), chord tones, BPM, and swing amount. When the context changes, every generator adapts simultaneously. The architecture keeps the music coherent even when parameters shift mid-phrase.

Here's the pivot that made Conductr possible as a hackathon entry. I had a week. My original plan was to demo this on actual hardware such as an ESP32 or similar microcontroller sending MIDI to real synthesizers. But I didn't have time to build the hardware enclosure, solder the circuits, and debug the electronics. So I made a practical decision: compile the C engine to WebAssembly and deploy it as a web app. The C code stays exactly the same. It just runs in a browser instead of on a chip.

The web stack ended up being pretty simple: vanilla JavaScript (no React, no framework), Web MIDI API for connecting to hardware synths, Web Speech API for voice commands, Three.js for a 3D visualization of the musical activity, and Vite for bundling. That's it.

The beautiful part is that the hardware path isn't dead. It's just deferred. The same C engine that compiles to WASM today can compile for an ARM Cortex-M tomorrow, or wrap into a VST plugin next month. Writing it in C with zero heap allocation was an investment in portability.

### The Engine Never Waits for the AI

This is the architectural insight I'm most proud of, and honestly, the reason I think Conductr won.

![Conductr architecture](../../../public/blog-img/conductr-architecture.png)

The system operates on three distinct timescales:

- **The C engine** runs at roughly 15 milliseconds per step. This is the note generation loop and the heartbeat of the music. It must be rock-solid and deterministic. You can't have a drum hit arrive late because a network request is pending.
- **The performance analyzer** runs every 4 seconds or so. It looks at what the user is playing such as pitch range, velocity, note density, rhythmic patterns then extracts a set of musical metrics.
- **Claude Opus 4.6** receives those metrics every 8 seconds and returns arrangement decisions: change the scale, shift the energy level, add swing, thin out the drums, transpose the bass.

The critical design principle: **the engine never waits for the AI.** Opus operates as a conductor, not a performer. It shapes the *next* phrase, not the current one. When Opus returns new parameters, they get queued and applied at the next musically appropriate boundary. The start of the next bar, typically.

And here's the fallback that makes it all work: when the API is unavailable because of slow network, rate limit, or just turned off, then a rule-based director takes over. It makes simpler arrangement decisions based on the same performance metrics. The music never stops. The AI makes it better, but the system doesn't depend on it.

I'll be honest about one thing. Using Opus 4.6 for this is overkill. A smaller, cheaper model could probably handle the arrangement decisions just fine. But the hackathon brief was "Built with Opus 4.6" and the theme literally demanded it. Sometimes you follow the brief to win, and worry about optimization later. (I can always swap to Haiku for production use.)

[Demo video](https://www.youtube.com/watch?v=X6CqJoyj0kI)

### What I Learned and What's Next

Building Conductr in a week taught me a few things worth sharing.

**Follow the hackathon brief.** This sounds obvious, but many submissions I saw were impressive engineering that didn't clearly showcase the model doing something unexpected. The judges wanted to see creative exploration of Opus 4.6, so I made the AI conduct a live band. Show the model in an unexpected context, not just another chatbot or code generator.

**Separate concerns by timescale.** This is the biggest technical lesson. When you have components that run at very different speeds, like a 15ms audio loop and an 8-second AI call, don't make the fast loop wait for the slow one. Give each timescale its own responsibility and let them communicate through shared state. This pattern shows up everywhere in real-time systems, and it's the reason Conductr feels responsive despite depending on an API call that takes seconds.

**Write portable code.** The C engine runs in a browser today. It'll run on a microcontroller tomorrow. It could become a VST plugin or a mobile app. None of that would be possible if I'd written it in JavaScript from the start. Choose your core language based on where the code needs to go, not where it is right now.

**Your weird combination of interests is your edge.** I've been writing about code and music on this blog for over a decade. Individually, neither my C programming skills nor my music production knowledge are exceptional. But the combination of someone who builds Eurorack modules *and* writes WebAssembly *and* understands MIDI *and* has opinions about algorithmic composition, that specific intersection is rare. Your unusual mix of interests isn't a distraction. It's your competitive advantage.

So what's next? I want to make Conductr a real hardware product. A standalone box with MIDI in and MIDI out that sits next to your keyboard and arranges a band in real time. The C engine is already there. The AI integration is proven. Now it's about circuit design, enclosure, and turning a hackathon prototype into something you can put on a desk.

The code is open source at [github.com/nanassound/conductr](https://github.com/nanassound/conductr). If you sit at that intersection of code and music, or if you're just curious about real-time AI architecture, I'd love for you to check it out. Pull requests welcome, weird ideas even more so.
