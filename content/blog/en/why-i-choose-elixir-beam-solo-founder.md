---
title: "Why I Choose Elixir and BEAM as My Main Stack as a Solo Founder"
date: 2026-03-04
categories:
- Programming
summary: "After twelve years of dating programming languages, I found the one. Here's why Elixir and the BEAM ecosystem cover everything I need as a solo founder."
---

Back in 2014, I wrote [an article about my relationship with programming languages](me-and-programming-languages.md). I described each language as a romantic partner. Erlang was "the girl who can blow my mind in the first date." Her syntax was bewildering, the OTP framework was hard to understand, and after three months, I gave up.

But here's the thing about breakups. Sometimes you learn exactly what you want from the next relationship.

After years of writing Clojure, functional programming concepts finally clicked for me. Pattern matching, immutability, thinking in data transformations. It all became natural. Then I found Elixir, a language that runs on the same BEAM virtual machine as Erlang but with a friendlier syntax and a richer ecosystem. It was like meeting Erlang's cooler younger sibling who actually knows how to have a conversation.

Today, Elixir and the BEAM ecosystem cover almost everything I need as a solo founder. Web apps, microcontrollers, embedded Linux. One language across three platforms. Let me explain why this matters.

### One Language, Three Platforms

The biggest advantage of Elixir for a solo founder isn't any single feature. It's the surface area it covers.

For web development, I use [Phoenix](https://www.phoenixframework.org/). It gives me server-rendered HTML with LiveView, real-time WebSocket features, REST APIs, and background job processing all in one framework. I'm building [playasynth.com](https://playasynth.com) using Phoenix with my business partner in Finland. I also built my wife's pet hotel booking system with it, and a social media competitor monitoring tool. Phoenix handles all of these without needing a separate backend framework, a separate WebSocket server, or a separate task queue.

For microcontrollers, there's [AtomVM](https://www.atomvm.net/). It runs BEAM bytecode directly on ESP32 chips. I built midiMESH, a wireless MIDI mesh network using AtomVM, and gave a [talk about it at FOSDEM 2026](https://fosdem.org/2026/schedule/event/QQRETA-midimesh_network_midi_with_elixir_on_esp32_via_atomvm/). Yes, the same language I use for web apps also runs on a tiny microcontroller.

For embedded Linux, [Nerves](https://nerves-project.org/) lets me build firmware for Raspberry Pi using the same Elixir tooling. Same language, same package manager, same testing framework.

The AtomVM creator, Davide Bettio, even [wrote about midiMESH in his Substack](https://bettio.substack.com/p/fosdem-was-a-blast) after my FOSDEM talk. As he put it, "Elixir + AtomVM can help web developers become makers without having to throw away the stack they already enjoy." That's exactly my experience.

Why does this matter? Because cognitive overhead is the real enemy when you're building alone. Every time you context-switch between languages, you lose time reloading syntax rules, library conventions, and debugging patterns into your brain. With Elixir, I just think about the problem, not about which language I'm in.

### Concurrency That's Already Built In

This is the part that makes BEAM truly special.

In most languages, concurrency is an afterthought. Python has the GIL, so true parallelism requires multiprocessing with all its complexity. Node.js is single-threaded, so CPU-heavy work blocks everything unless you offload it. Go has goroutines which are nice, but you still manage channels and mutexes yourself. In all of these, you're fighting the runtime to do things concurrently.

In the BEAM, concurrency is just how things work. Every process is lightweight (a few kilobytes of memory), isolated, and supervised. Need to handle 10,000 simultaneous WebSocket connections? Phoenix just does it. Need a background job that monitors a competitor's social media every hour? Spawn a GenServer. Need to retry a failed task with exponential backoff? OTP has patterns for that built into the runtime.

For my pet hotel booking system, I have real-time availability updates, email notifications, and payment processing all running concurrently. In a Node.js or Python world, that's at least three separate services plus a message broker. In Elixir, it's one application with supervised processes. One deployment. One thing to monitor.

The "let it crash" philosophy changes how you think about errors too. Instead of writing defensive try-catch blocks everywhere, you let individual processes fail and restart cleanly. The supervisor tree handles recovery automatically. This sounds scary at first, but it produces more reliable systems with less code. Erlang was built for telephone switches that needed 99.9999% uptime. That reliability comes for free with the BEAM.

I don't have a DevOps team. I don't want to manage Redis, RabbitMQ, and a separate worker fleet. The fewer moving parts in my infrastructure, the better I sleep at night.

### Why Elixir Works Well with LLM-Assisted Coding

I [won Anthropic's hackathon](winning-anthropic-hackathon-conductr.md) recently and I code with LLMs daily. So I have some practical observations here.

Elixir's style naturally produces small, pure functions. Each function takes input, transforms it, and returns output. No hidden state mutations. This makes it easy for LLMs to generate and test code in isolation. Pattern matching creates clear input/output contracts that LLMs can follow. And the pipe operator (`|>`) makes code read as a linear chain of data transformations, which LLMs generate surprisingly well.

LLMs know Elixir much less than Python or JavaScript. The training data is simply smaller. But I've noticed that generated Elixir code tends to be more correct on the first try. I think the language's structure forces clearer thinking, even for an AI.

### The Trade-offs

No stack is perfect, and I'm not going to pretend otherwise.

Phoenix LiveView is great for most interactive UIs, but not everything. When I need complex client-side interactions with heavy state management, I still reach for React.

The ecosystem is smaller than npm or PyPI. Sometimes the library you need doesn't exist, and you have to write it yourself. This is fine when you enjoy building things (I do), but it's worth knowing upfront.

Hiring is harder if you ever grow beyond solo. The Elixir developer pool is much smaller than JavaScript or Python. For now, this doesn't affect me. But it's something I keep in mind.

### Finding the Right Partner

The lesson here isn't "you should use Elixir." Your situation is different from mine. The real lesson is this: if you're building alone, find one ecosystem that covers your surface area and go deep. The productivity you gain from mastering one set of tools, one way of thinking, and one community is worth more than having the "best" tool for each individual job.

Back in 2014, I was dating every programming language I could find. Twelve years later, I finally found the right partner. She runs on the BEAM, she speaks in pipes and pattern matches, and she follows me from web servers to microcontrollers without complaining.

If you're a solo founder still shopping for your main stack, I hope this gives you something to think about. And if you're already in the Elixir world, I'd love to hear what you're building with it.
