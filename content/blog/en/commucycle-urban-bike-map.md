---
title: "Commucycle: Urban Cycling Map"
date: 2023-10-10
categories:
- Programming
summary: "With the help of AI, I build and release an iOS app for commuting by bicycle worldwide."
---

In the past few months, I work on a side project called [Commucycle](https://www.commucycle.com). It is an iOS app that helps you find the best route to commute by bicycle, and it works worldwide. It is available for free on the [App Store](https://apps.apple.com/us/app/commucycle-urban-cycling-map/id6463171771?itsct=apps_box_promote_link&itscg=30200).

![The landing page of Commucycle](../../../public/blog-img/commucycle-marketing.jpg)
*Download Commucycle on App Store*

Here's the story behind why I built this app.

### Scratching my own itch

Since I moved to Estonia two years ago, I ride the bicycle to go everywhere. It’s my go-to choice of transportation. I ride it in all seasons, even in the winter. It’s fast, cheap, and healthy. Whenever I travel to other cities in Estonia and neighbouring countries, I like to bring my bicycle with me as long as possible.

I usually use Google Maps to find the best route to go somewhere I have never been. However, Google Maps doesn’t has a bicycle mode in Estonia. So, I usually use the walking path instead. It works, but it’s not ideal. The walking mode doesn’t know that I can ride on the bicycle path, so it often gives me a route that is not optimal for cycling.

I decided to solve this problem. After researching where to get data for the bicycle path, I chose the service of [Stadia Maps](https://stadiamaps.com). They have an API that can calculate the best route for bicycle. Their routing API is based on [Valhalla](https://github.com/valhalla/valhalla), an open-source routing engine for OpenStreetMap data.

### Why building for iOS?

I feel bored with web development. I have been doing it in the last 13 years. I want to try something new. I have been using Apple devices since 2010. I use MacBook Pro, iPad, iPhone, and Watch. I did iOS development in the past when Apple still used Objective-C as its prime programming language. So, I want to try iOS development again.

Nowadays, Apple uses Swift as its programming language for iOS development. I have never used Swift before. So, I have to learn it from scratch. Luckily, in 2023, the artificial intelligence is so advanced. I am able to learn Swift and SwiftUI in relatively short time with the help of Github Copilot.

Here’s the thread on Twitter (X) about my experience using Github Copilot to build this app.

<blockquote class="twitter-tweet"><p lang="en" dir="ltr">Since Apple and Google map doesn’t has bicycle route for Estonia, so I decide to create my own app and solving my problem. Here’s how I learn iOS development from zero in 2023: [pic.twitter.com/mpYkjcKBGb](https://t.co/mpYkjcKBGb)</p>&mdash; Asep Bagja 🍍 (@bepituLaz) [July 28, 2023](https://twitter.com/bepituLaz/status/1684992165099794432?ref_src=twsrc%5Etfw)</blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>

### What's next?

I will continue to improve this app and build the companion app for Apple Watch. I must say sorry to Android users. I don’t have plan to develop the Android version of this app. I don’t have any Android device, and also I don’t have any experience in Android development. So, I will focus on iOS development and keep scratching my own itch.