# 2026-03-10 Meeting

### Meeting Agenda

**Time:** new meeting #10, 3/9 9pm Monday San Diego time
- company update, raise
- LLaMA training
- viz
- drivers
- IMAGE=1
- tiny specs
- assign, divmod
- other issues, bounties, any Comma complaints

### Audio

[Youtube Link](https://www.youtube.com/watch?v=SQAUM4KsHmc)

### Highlights

- **[Company Update / Raise Strategy](#geohot-000004)**: Geohot lays out the fundraising thesis: TinyCorp should move up the stack from selling cheap flops to hosting machines and ultimately selling tokens, where margins are much higher.
- **[Data Center Plan via Bitcoin Mines](#geohot-000004)**: The proposed infrastructure path is to buy undervalued Bitcoin mines and convert them into low-cost tier-one data centers at roughly the 5–10 MW scale, avoiding expensive traditional colo.
- **[Fundraising Status](#geohot-000004)**: TinyCorp is raising **$20M at a $200M valuation**, up from the prior **$5M on $50M** round, backed by shipped product progress, a **$2M AMD contract**, and TinyGrad advances.
- **[AMD Relationship Is Strategically Critical](#geohot-001153)**: Geohot stresses that the AMD contract matters beyond its direct value, because a strong relationship could unlock favorable RDNA5 GPU pricing and swing the company’s economics by millions.
- **[LLaMA Training Priority: Get One Step Working](#geohot-001232)**: For LLaMA training, the immediate milestone is simply getting a training step to fit and run; only after that should the team optimize issues like speed and gradient checkpointing.
- **[Viz Sprint Goals](#geohot-002023)**: Geohot sets the sprint goal for visualization work: finish real-time support and CDNA support, while aligning naming with AMD’s official terminology wherever possible.
- **[Driver / Memory Planner Refactor Progress](#geohot-002544)**: Nimlgen reports memory issues and per-track speed issues are fixed, with a refactor toward `ops custom function`; Geohot also wants the memory planner logic extended to `DEFINE_LOCAL`.
- **[IMAGE=1 Bottleneck: Padding and Invalid Semantics](#chrism-003003)**: The main remaining IMAGE=1 issue is expressing “don’t care” padded data efficiently, since writing explicit zeros hurts performance and current padding semantics force unnecessary work.
- **[Invalid Should Be Powerful but Dangerous](#geohot-003914)**: The team agrees `invalid` can be introduced as a footgun-heavy primitive: useful for optimization, allowed to propagate through expressions, and not necessarily something that should raise errors if it collapses into a no-op kernel.
- **[Core Spec Direction: `call` and Simpler Multi-Device Semantics](#geohot-004453)**: Geohot says the new core spec is converging, with `call` viewed as a major simplification win for graph size and future JIT 2.0 work, plus a cleaner model for multi-device buffers by making sharding explicit in shape.
- **[Div/Mod Rewrite Work Improved Performance](#chenyu-004948)**: Chenyu says consolidating and strengthening div/mod simplification fixed discrepancies and made OpenPilot with image2 about **7% faster**.
- **[Image 1 and Image 2 Removal Is This Sprint’s Goal](#chenyu-005228)**: Chenyu and Geohot align on removing both image-mode special cases this sprint, which should also eliminate the need for some of the current “correct div/mod” complexity.
- **[RDNA5 Discussion: Hope for High-VRAM AMD Cards](#geohot-005649)**: In closing, the team discusses rumored RDNA5 configurations, focusing on whether AMD may ship higher-memory variants like **72 GB**, which could be important for TinyCorp’s future systems.

### Transcript
##### **Geohot** [[00:00:00](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=0)]
Let's start with company update.

##### **Geohot** [[00:00:04](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=4)]
Great. Yeah, so I've kind of been thinking like, there's no reason that we should own,

##### **Geohot** [[00:00:19](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=19)]
we can make our own demand, basically. Like, there's no reason that we should own only, if we really have the cheapest flops, there's no reason that we should only own part of that stack. Why don't we own as much of that stack as possible? So there's a huge marketplace on OpenRouter for tokens. I think that this market is going to grow massively in the next couple of years. I think that's a pretty generally accepted thesis. You can look at all the people lining up to install Open Claw. And like, look, even if it's fake, the world market for tokens is about to explode. So tokens are kind of like, you can think about all the places. So TinyCorp right now, if you buy a tinybox red, that's actually the cheapest flops per dollar you can buy. And that's only like, why stop there? Why would we not also host that tiny box for you? And then why stop there? Why would we not run the application that you're going to run on that tiny box for you? And if you're just going to end up running an LLM, we should be selling you tokens. Now, I'm not saying we don't sell the other things. We sell all of them. But we progressively make more margins. But computers are a 20-30% margin business. Hosted computers, 50% margin business. Tokens, 70-80% margin business potentially. So what do we need in order to do that? We need basically a world-competitive, globally competitive, cheap place to plug in tiny boxes. Then you start asking, okay, what scale should we do this at? So Comma has been operating at the 500 kilowatt scale for the last couple of years, just kind of finally filling that data center up. At what scale does, like, so you don't want to do it at 500 kilowatt scale because you have fixed costs. You've got to get security for the building. You've got to get maintenance people up there. You know, whether you're driving a truck, it doesn't matter how many computers you put in it. So the question then is: where is the next scale breakpoint? Where is the scale breakpoint where you can still fit all the computers in one truck, where your cost of security and stuff is amortized? And the answer to that is probably somewhere around five to 10 megawatts. So five to 10 megawatts costs about a million dollars a megawatt. So that's a lot of money. So you have to be able to fit a site out the way we're going to fit it out. We're way cheaper than everybody else because we're not doing tier-three data center stuff. You look at the cost of colo and it's astronomical. I went to Washington last summer and oh my God, these people want 30 cents a kilowatt hour to run your things. I mean, we're literally running it at the same price in San Diego. And that's not even like they have all these fees they tack on and stuff. It's awful to deal with these kinds of people. And the reason they can act that way is because of overvaluations that are overly inflated, and AI companies have come in and basically pre-bought all the capacity. But there's a great way right now to get capacity, and that is Bitcoin mines. So Bitcoin right now is low. Bitcoin mines are underwater. There has never been a better time to buy up a Bitcoin mine. Get it out as a tier-one data center. We're not going for tier three here. 99.9% of uptime beats Claude. So yeah, build out a tier-one data center, have everything ready to plug in five to 10 megawatts of stuff the second the unit economics makes sense. And then, as soon as the unit economics makes sense, we build tiny boxes not for customers, but for ourselves, and then sell the tokens on a marketplace like OpenRouter or something competitive. That's basically the pitch. We're raising $20 million on $200 million. Our last round was five on 50. Since then, we've built a product and shipped it. We have a $2 million contract with AMD. And we've made tons of progress on TinyGrad that will actually enable us to start to be able to use this cheaper hardware. The way that we're going to beat everybody else in the space is two things. One, we don't build tier-three data centers. We build tier-one data centers. And two, we don't buy Nvidia chips that already have the entire margin baked into them. If you're buying an H100, if you're buying a B200, that chip has 80% margin. You can't make money. It's already gone, right? So we want to buy chips with 30% margin and then take all that margin for ourselves, basically, because tokens and flops are a commodity. Tokens really are a commodity. Nobody who's buying a token on OpenRouter cares if that's an AMD token, Nvidia token, or a SambaNova token. So yeah, commoditize the path to flops at every scale we possibly can. That's the raise.

##### **Geohot** [[00:05:25](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=325)]
Didn't get much sleep last night being on the phone with people. There's the pitch.

##### **Geohot** [[00:05:52](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=352)]
Yeah. Yep. Oh yeah! We have lots of people who want to give us money. It's a question of who we want to take money from. Yeah. So when do we expect it to close? Realistically, I'm back in America in April.

##### **Geohot** [[00:06:06](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=366)]
It's probably not going to close before then. Any questions for people in this meeting? Right here.

##### **Chenyu** [[00:06:18](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=378)]
I'll start a pitch sheet. Feel free to post in general channel. And while you are doing so, we can continue with our agenda.

##### **Geohot** [[00:06:29](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=389)]
Start with LLaMA training. I don't know how stable my internet is. My current download speed is 100 kilobits per second. I hope it's working. I can hear you if you're talking. It's not working. Is it better? Uh-huh. Hello? Chenyu? Working. Yep.

##### **Chenyu** [[00:11:23](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=683)]
Yeah. Can you just pause it? I will run it later.

##### **Geohot** [[00:11:25](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=685)]
Yes. I'll post the command.

##### **Geohot** [[00:11:28](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=688)]
Yeah. Because then other people can also try that. See if it applies for the copy thing or whatever. Yeah. I will do that later at the airport because where I'm at right now, the internet is really bad.

##### **Geohot** [[00:11:53](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=713)]
I want to again reiterate the importance of the AMD contract. The importance of the AMD contract is that another way that we can be more competitive than anybody else is that if we can get AMD to give us a good deal on RDNA5 cards. It's important that we do a good job on this relationship. I'm going to go speak to them. I'm going to go speak at their thing and I should reply to their thing. They want me to go speak at their thing. This relationship is very important to us as a company and it could potentially be something like a $5 million swing. Even more than the value of this contract.

##### **Geohot** [[00:12:32](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=752)]
So, yeah. We have to get one of these. We have to get one of the four of them. Yes. All right. If we get a step this sprint, we're looking good. Yeah. Are we? We got a step? I think so. Yeah. It would take a month. I'm pretty confident that we can get a step. It might be very slow.

##### **Chenyu** [[00:12:58](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=778)]
Well, why?

##### **Geohot** [[00:13:00](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=780)]
I'm confident we can get a step.

##### **Chenyu** [[00:13:01](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=781)]
Okay. Let's get a step first.

##### **Geohot** [[00:13:02](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=782)]
Let's get a step first and then like why is it... It's going to step first and then we can figure out why it's slow. I'm confident in our... Look, if we don't have to do too much like gradient checkpointing, I'm confident in our jam and flash attention being fast. I'm confident in our... The gradient offloading thing can be rewritten so quickly if that's at all an issue. So, I'm not worried about that. I guess I'm only worried about it fitting in memory and not needing to do too much gradient checkpointing. It's like too much gradient checkpointing. Yeah.

##### **Geohot** [[00:13:35](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=815)]
I do think we need to do a bit of gradient checkpointing.

##### **Geohot** [[00:13:39](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=819)]
That depends on how much. How much are we recomputing, right? If we're recomputing nothing, we have high throughput kernels. You know, everything's good. But...

##### **Nimlgen** [[00:13:51](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=831)]
Yeah.

##### **Chenyu** [[00:13:51](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=831)]
Let's resume this discussion after we have a step that fits.

##### **Nimlgen** [[00:13:56](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=836)]
Right. Yeah.

##### **Geohot** [[00:13:58](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=838)]
First thing is fitting a step.

##### **Chenyu** [[00:14:00](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=840)]
That sounds good. Just post the comment somewhere. Go from there. Let me know if you hit other assign issues or item issues, like BUFFERIZE. Yes. BUFFERIZE assign has so many issues. I just replaced one hack with a better hack.

##### **Geohot** [[00:14:20](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=860)]
Right. Okay. Sounds good. Okay. Next is this.

##### **Qazalin** [[00:14:28](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=868)]
Yeah. Last week, I spent a lot of time looking into real time, putting seconds in the SQTT. It's almost done. It's almost done. It's in the branch for RDNA. And...

##### **Geohot** [[00:14:45](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=885)]
Yeah.

##### **Geohot** [[00:14:46](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=886)]
Almost done. Have you changed the names over to the official ones?

##### **Qazalin** [[00:14:50](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=890)]
I am starting to do that. Yeah. The names are actually some of ours are better.

##### **Geohot** [[00:14:56](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=896)]
No, ours are definitely not better. Why do you think ours are better?

##### **Qazalin** [[00:15:00](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=900)]
Yeah, there's some stuff like `bit8`. That's just bad. Some VOPs are nicer. But I've changed most of them, especially for RDNA 4, since those were wrong.

##### **Geohot** [[00:15:14](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=914)]
Okay. If you want to say they're nicer, really, like, at least have a comment with AMD's name.

##### **Qazalin** [[00:15:25](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=925)]
All right. Yeah. So, like, the ones that I'm mentioning are like: we call this, for example, `VALU_B4`, and they call it `VLU-4` or something.

##### **Geohot** [[00:15:39](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=939)]
Yeah, look, I'm okay with that if you just have a comment about how it's `VLU-4`. Okay. But it also somewhat seems like that repo might have been stripped of some real stuff. But

##### **Qazalin** [[00:15:54](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=954)]
Oh, it's definitely stripped of some real stuff. I don't see ALU exec or VALU exec at all mentioned.

##### **Geohot** [[00:16:01](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=961)]
Which is crazy. I didn't see those either. Did you figure out how...? I mean, it is working for their stuff. That stuff has to be using ALU exec and the VALU execs, right?

##### **Qazalin** [[00:16:11](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=971)]
No, it's not. It's patching. Yeah. So everything that's about the quote unquote duration and stall stuff is like in the stitcher layer later, that's like patching from the ISA. That's why when you put vnop after and after over and over, you'll get like right timestamps but wrong everything else.

##### **Geohot** [[00:16:34](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=994)]
Wait, but is that true in the real RGP profiler too?

##### **Qazalin** [[00:16:39](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=999)]
Yeah, yeah. I read the code. It's like when you put vnop.

##### **Geohot** [[00:16:43](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1003)]
Is it true in the closed source one too? Oh, the closed source one?

##### **Geohot** [[00:16:49](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1009)]
Yeah.

##### **Qazalin** [[00:16:50](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1010)]
Oh, you mean compare the open source and the closed source. I see.

##### **Geohot** [[00:16:54](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1014)]
I'm saying: is the closed source one using VALU exec or not? Because, yeah, I thought that was weird that they didn't have it.

##### **Geohot** [[00:17:04](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1024)]
Yeah, I didn't check that. I have to. Yeah.

##### **Qazalin** [[00:17:10](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1030)]
It's weird that they don't have it.

##### **Geohot** [[00:17:13](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1033)]
Yeah. I mean, they might just get the stall with the dispatch, but, you know, I agree. It's weird. They don't have it. I don't know. How's CDNA viz coming?

##### **Qazalin** [[00:17:21](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1041)]
Oh, God. CDNA... I'm working on it. It's complicated. I mean, the timestamp patching stuff.

##### **Geohot** [[00:17:29](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1049)]
Yeah, I don't really care if it matches perfectly. I saw your algorithm re implementation of what they were doing. Look, if it's a few cycles off, I don't even know if their thing's correct.

##### **Qazalin** [[00:17:41](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1061)]
Same, same, same, same. It doesn't. So there's like a packet that's like patch this. And then you have to buffer a bunch of waves. You can't like yield the packets as they come in. You have to like buffer them in memory. Oh, I think about it.

##### **Geohot** [[00:18:02](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1082)]
Yeah, I don't think we should have all this complexity. I think there's a chance that our stuff is just better than theirs. Same, same. Just yeah, draw the draw the real stuff. Um,

##### **Qazalin** [[00:18:13](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1093)]
I'm also interested in seeing if CDNA has an exec, because I only saw issue in CDNA. So there's an issue and then there's a confirmation of that instruction. But there's no exec, like VALU exec, which I'm suspicious of. There might be an undocumented one again, because exec wasn't in the code either.

##### **Geohot** [[00:18:39](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1119)]
So I would guess that CDNA has one that just isn't documented. How'd you get the clock speed for real time?

##### **Qazalin** [[00:18:46](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1126)]
Oh, I read the bias and also sampled the registers from MMIO to confirm it.

##### **Geohot** [[00:18:54](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1134)]
Okay, you confirmed it. You did something to confirm it, and it really doesn't change.

##### **Qazalin** [[00:19:00](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1140)]
So the clock speed, the RLC, does not change. It's steady at about 200 megahertz. The shader clock might change, which is, I think, the reason why RDNA gives you a stream about every 4000 cycles. It's the calibration. So CDNA doesn't. Interestingly, it does give you a calibration.

##### **Geohot** [[00:19:29](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1169)]
CDNA has... the whole thing is real time. Yeah, no, I know the packet you're talking about for RDNA. Okay, cool. So that thing runs at 100 megahertz. Yeah, makes sense.

##### **Qazalin** [[00:19:38](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1178)]
Yeah, the reference clock like runs on 100. The other one. Is. Pretty stable. Like if you plot it, it's linear. It's perfectly linear, but I don't know.

##### **Geohot** [[00:19:49](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1189)]
You left the cycles in too, right? It has both cycles and the real time.

##### **Qazalin** [[00:19:54](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1194)]
Uh, so the real time. Yes, it only has the last 36 bits of the real time.

##### **Geohot** [[00:20:02](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1202)]
Uh, yeah, but my point is the bar should have both the cycles and the real time because the shader clock might change.

##### **Geohot** [[00:20:12](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1212)]
Yes. The shader clock might change. It doesn't, but it could. Yeah.

##### **Nimlgen** [[00:20:19](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1219)]
Cool.

##### **Geohot** [[00:20:23](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1223)]
All right. Yeah. So this sprint: finish up real time and CDNA, and use as many AMD names as possible.

##### **Qazalin** [[00:20:30](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1230)]
Using as many AMD names as possible. Yeah. Makes sense. I'll get to CDNA more. Uh, I see that your decode loop supports CDNA too, supposedly because it's not packet-based, right?

##### **Geohot** [[00:20:48](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1248)]
But it is packet-based. AMD just doesn't understand that it is. The loop supports both. The RDNA one clearly was developed after the CDNA one, and they talk about the CDNA one differently, but the RDNA one is flexible enough to encapsulate what the CDNA one is.

##### **Geohot** [[00:21:08](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1268)]
We shouldn't have two decode loops. I know that their repo talks about this differently, but they just didn't understand what they were doing when they went to CDNA one. It's the same.

##### **Qazalin** [[00:21:27](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1287)]
Oh, no, probably sample some real stuff. See if the timestamp patching actually makes a difference.

##### **Geohot** [[00:21:36](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1296)]
Yeah, as long as it's close. It doesn't matter. Yeah.

##### **Qazalin** [[00:21:41](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1301)]
I'm also briefly considering putting all the structs in autogen. Not going to be easy because the code is in C++.

##### **Geohot** [[00:21:51](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1311)]
I don't think that's worth it. Just copy it. Yeah, I think they're simple enough that we just write our own.

##### **Nimlgen** [[00:21:59](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1319)]
Okay.

##### **Geohot** [[00:22:01](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1321)]
Yeah, they're not. Just simple. There's only like 12. Uh,

##### **Geohot** [[00:22:12](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1332)]
One of the other distinctions, and why I'm okay with not using autogen for this, is you have to ask the question: is this in software or hardware, right? But for something like `libc`, obviously we have to use autogen because `libc` can change. It's a software package. It could be updated. It's not like AMD can update the RDNA3 SQTT packets.

##### **Geohot** [[00:22:38](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1358)]
They can't.

##### **Nimlgen** [[00:22:40](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1360)]
How?

##### **Geohot** [[00:22:43](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1363)]
Micro-update? With what? No, not micro. Yet. Uh, yeah, I strongly doubt they could update it.

##### **Qazalin** [[00:23:02](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1382)]
Yeah, the reason why I think it is because real time is actually a pretty new thing. But maybe the decoder is a new thing, and maybe it's just a packet.

##### **Geohot** [[00:23:15](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1395)]
Yeah. Yeah, I'd be very surprised if they could update it.

##### **Geohot** [[00:23:19](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1399)]
But I'm curious if there's any evidence that they can, but I doubt it.

##### **Qazalin** [[00:23:26](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1406)]
I'll look at it because I am suspicious of one packet. Oh, please.

##### **Geohot** [[00:23:33](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1413)]
The side thing on Viz looks nice.

##### **Geohot** [[00:23:35](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1415)]
I would just try to fit those on one line if you can like with the address in the instruction.

##### **Geohot** [[00:23:41](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1421)]
I can't. I tried. I tried. I know, like, you have a lot of zeros that you don't need. Uh, so you actually do, because your PC can get larger and it gets ugly. I don't know, whatever. You think about that.

##### **Qazalin** [[00:24:08](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1448)]
I broke it into two lines. I think two lines is reasonable.

##### **Geohot** [[00:24:12](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1452)]
It's too many lines.

##### **Qazalin** [[00:24:22](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1462)]
Two lines. I mean, the sidebar is tiny.

##### **Geohot** [[00:24:28](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1468)]
Make it bigger. That's so many lines. All right, cool. Yeah. Okay. Later. I'm thinking about it more. Also,

##### **Qazalin** [[00:24:42](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1482)]
Also, there's a backtrace in the user device now. I know you asked for that.

##### **Geohot** [[00:24:46](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1486)]
Oh,

##### **Geohot** [[00:24:47](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1487)]
Yeah. I saw you mention that.

##### **Geohot** [[00:24:49](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1489)]
Yeah, that's nice. That's great.

##### **Qazalin** [[00:24:50](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1490)]
Yeah, you'll see it in exactly the tensor call.

##### **Geohot** [[00:24:56](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1496)]
That's exactly the tensor call that created whatever that thing was. Yeah, that's nice. That's all for me. That's good. Next, IMAGE=1. What? It's just drivers. Sorry. My bad. Yeah.

##### **Nimlgen** [[00:25:24](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1524)]
So memory issues should be fixed. Speed on each track also was fixed. And also, emergency refactor: I removed ops and tags, and now we have ops custom function.

##### **Geohot** [[00:25:42](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1542)]
Yeah.

##### **Nimlgen** [[00:25:44](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1544)]
No, I think ops custom function is a lot better. I briefly read the refactor.

##### **Geohot** [[00:25:45](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1545)]
So confirming that custom function is like source 0 of a call, right?

##### **Geohot** [[00:25:59](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1559)]
Yeah, yeah, yeah. Great. Yeah. I mean, I think hopefully this API makes sense for all things that look like that. You can put anything you want in custom function. In fact, there's even a world in which copy can become custom function. Maybe not copy in the big graph, but as soon as we lower copy to... right?

##### **Geohot** [[00:26:17](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1577)]
Like the custom, like SDMA could be a custom function. That makes sense. We think it's better to keep a copy. Do you think it's better to keep copy as like the way that it is, or switch to a good like custom function, like SDMA? Uh, I don't know. I mean,

##### **Nimlgen** [[00:27:09](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1629)]
I think it's fine as it is, but actually, I mean, semantically it's like, yeah, it's the custom function. I mean, it's the same idea as NK tag.

##### **Geohot** [[00:27:20](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1640)]
The other advantage to using custom function is then we could use both SDMA engines.

##### **Geohot** [[00:27:28](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1648)]
Yeah. Yeah. I don't know. It's just an idea, but, uh, uh, yeah, cool. We'll, we'll talk about it when you get here.

##### **Nimlgen** [[00:27:37](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1657)]
Yeah. And I mean, for the memory, for the new memory planner, I ported it as a rewrite rule. And actually it works in schedule, but I think we need JIT 2.0 to have the same memory usage in JIT. So basically, because we have several realizes, we would have to... We can have several realizes inside JIT. Yeah, that's the main problem. Either we keep two, or we have some problems with memory usage.

##### **Geohot** [[00:28:20](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1700)]
Yeah. I think before JIT 2.0, I mean, I think it would be pretty easy to kind of like, we can, uh, we can mess with the realizes. We can like not do the realizes if you're inside of tiny JIT, like even with the JIT we have now and just pin the realizes till the end. Um, I think I call it like a qualify or something. So we can do the, we can basically do the realize inside the JIT, but it would still stay in the graph. Like we'd lower it to the point that it's the linear and that, uh, I don't know. Or we could just rip off the bandaid and just get to 2.0 working. Um, I don't know. No, I think, I think like it's a worthwhile step beforehand to blacklist the use of

##### **Geohot** [[00:29:07](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1747)]
realize in JIT. I think that's something we realize well at the end.

##### **Geohot** [[00:29:21](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1761)]
Yeah. Yeah. I don't know. We'll have to think this through right now. But, um, cool. I'm glad memory planner is in the scheduler. I also want to move, maybe you want to take this, define local to buffer.

##### **Geohot** [[00:29:37](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1777)]
So that it works for DEFINE_LOCAL as well. Yeah, I can do that. Anything else? No.

##### **Nimlgen** [[00:29:57](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1797)]
Cool.

##### **Geohot** [[00:29:58](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1798)]
See you soon. Next, IMAGE=1.

##### **Chrism** [[00:30:03](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1803)]
Yeah. Uh, yeah. So I think the last big thing for image one is invalid in Tensor. Um, yeah, I can explain why we need that. Which is, you know, if you've used `pad`, then you're forced to put zeros everywhere. And you don't want to have to write all the zeros on the extra place you don't care about, because you never read them. So we need some way to express "don't care about this extra data." And you could use a partial assign, but the problem is that means you need to assign into an existing buffer. And if you don't know where the buffer is going to be, then you can't assign it. If you don't already have a buffer, there's nothing to assign it to. Yeah, that's the deal. I think it's all coming from this `pitch_add` thing, where we add a little bit of extra stuff to the pitch in the case of `image=2`, just to mess with the alignment. And yeah, when you comment out the `pitch_add` stuff, we get the same performance in image 1 as image 2. So that seems to be where all the performance difference is coming from. And the problem is that right now, if I add that and we write it down, if you write all zeros there, then you spend all this time writing all these extra zeros. It's wasteful.

##### **Geohot** [[00:31:43](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1903)]
Why are there two more kernels? What other kernels?

##### **Chrism** [[00:31:46](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1906)]
They just come from the pad. So the `found_contiguous` hack can't see through pad. And we do extra padding right now in image 1.

##### **Geohot** [[00:32:01](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1921)]
Ah, I see.

##### **Chrism** [[00:32:02](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1922)]
OK. I profiled the difference, and it's like 0.05 seconds.

##### **Geohot** [[00:32:07](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1927)]
OK. So yeah, sounds like I got the assigned thing working. And then why is the wall time 30% more?

##### **Chrism** [[00:32:16](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1936)]
Yeah. I mean, choosing the best dimensions for the image is really expensive. I should probably figure out a better way to do this. But we just iterate all of them and see which one removes the most divmods.

##### **Geohot** [[00:32:33](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1953)]
Most div mods. OK. So that's what's, are you caching it?

##### **Chrism** [[00:32:37](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1957)]
Yeah. Should be caching. I can double check. But yeah.

##### **Geohot** [[00:32:42](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1962)]
I don't know. I think if you're running with a debug, just have it print some stuff for that. If it does that search and what it finds? Yeah. Is there any print in the debug if I?

##### **Chrism** [[00:32:52](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1972)]
No. But I think.

##### **Geohot** [[00:32:54](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1974)]
Yeah.

##### **Geohot** [[00:32:56](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1976)]
But cool. Yeah. Just confirm that it's that. Because we can't have, we got to make that the same.

##### **Chenyu** [[00:33:01](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1981)]
Yeah. So we would have a pad that's an actual pad, not the pad with const zero.

##### **Chrism** [[00:33:11](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=1991)]
Yeah. You could do that. I don't know if this is something that, the way that I was expecting people to use this is you have your mask and you do dot where, and then your values are invalid. But we could also expose this as a pad. Because our pad now is like pad with const.

##### **Geohot** [[00:33:32](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2012)]
Oh, you want it to be pad with const zero. I don't want to change the semantics. OK. I do not want to change the semantics of padding. Pad with const. No, padding. But padding with, so let's say you pad without, let's say you pad with invalid. How do you get zeros there? I don't know. It's like. No. I don't know how to use that.

##### **Chenyu** [[00:33:58](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2038)]
If you want to pad with zero, you just say pad zero. What does it mean to pad with zero? How does that work? What does that look like in UOps? I don't know. We just guarantee that if you do that, then when you access the value, it's guaranteed.

##### **Geohot** [[00:34:12](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2052)]
No, no, no, no, no. Pad should definitely be zeros. So then, but it's free, right? So then what the construction looks like when you want to do the invalid thing is that you have a, let's say I have a buffer that's 13 by 13. I want to pad 16 by 16. But I do a pad on it, which adds zeros. But that's not what I store. After that pad to 16 by 16, I do a where with a mask and invalid. It loses no performance. It's great. But I think it's much better to keep pads semantically,

##### **Geohot** [[00:34:40](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2080)]
meaning add zeros, and then you can get rid of those zeros later. Well, let's say it's invalid, right? If it's invalid, how would you express that? How do you express pad with const zero? A `where`? How?

##### **Geohot** [[00:35:21](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2121)]
What do you mean?

##### **Geohot** [[00:35:21](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2121)]
Oh, you want to write a where?

##### **Geohot** [[00:35:23](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2123)]
Yeah. You want to have it be invalid and then do the other thing where you have it do a where? Yeah, yeah. I definitely don't want to do that. Because the problem with that is, I will kind of match how we use valid in, you know,

##### **Geohot** [[00:35:34](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2134)]
No. Why should it be different? That's a pattern we currently have. The other one matches how we use invalid in UOp too, I think. Oh, you use it as a `where`? Yeah, yeah, yeah. We use invalid as a `where`. Pad doesn't add invalid. Pad adds zeros. Well, the other problem then is like, okay, so what's the derivative of pad zero? I mean, add zero.

##### **Geohot** [[00:36:14](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2174)]
Add zero, right? Like, yeah, we want to keep pad as pad zero. I really don't think we want to change that. And I really don't think we want to add an argument to pad.

##### **Chrism** [[00:36:27](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2187)]
Yeah, the only hang up I had while I was writing that is tensor indexing. You're right. It's, well, the problem is that we do tensor indexing with reduce over like you do a sum. I don't know.

##### **Geohot** [[00:36:44](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2204)]
I mean, as long as it solves your issue.

##### **Chenyu** [[00:36:49](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2209)]
Yeah. It's not clear if we introduce invalid in Tensor, like to what extent it should work, right? It has a weird dtype. Should it work with other dtypes? Yeah. And what do we define the dtype as? I don't know. I think it's a little bit of a mystery.

##### **Nimlgen** [[00:37:04](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2224)]
Yeah.

##### **Chrism** [[00:37:05](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2225)]
But anyway, I tried to add a test that was like: say you try to tensor-index with something that's partially invalid, like a tensor that you're using to index the other tensor is partially invalid. It makes the entire thing invalid because you're doing this reduce. And if anything in the reduce is invalid, then the entire thing is invalid.

##### **Chenyu** [[00:37:24](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2244)]
But then we start to add things in `tensor.py` that look data-dependent, like "check your data" and stuff, and we really don't want that. Yeah. No, for sure. For sure.

##### **Geohot** [[00:37:34](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2254)]
I don't understand how you can raise an error if you try to index with an invalid.

##### **Geohot** [[00:37:41](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2261)]
Yeah, but how can you know if it's invalid? What do you mean? Yeah, just when you render it. If the kernel at the end of rendering has an invalid left in it, raise an exception.

##### **Chenyu** [[00:37:52](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2272)]
How about that? Like, it has a kind of a multiple in tensor dot like, that's about five.

##### **Geohot** [[00:37:58](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2278)]
Just in rendering it. Sure. Like, there's some things you just can't write, right? Like, you can't write a kernel. Yeah. If I write something that says invalid plus one dot realize, what's your reason there?

##### **Chrism** [[00:38:08](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2288)]
Oh, you think you should raise an error and not just not do anything?

##### **Geohot** [[00:38:11](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2291)]
Maybe not do anything.

##### **Chrism** [[00:38:13](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2293)]
Well, okay. So like, say you have like a full of invalid, right?

##### **Geohot** [[00:38:17](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2297)]
I don't understand full of invalid. If I do, if I do, if I create a tensor with invalid as a const, I do that plus one. I do dot item on it.

##### **Chrism** [[00:38:30](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2310)]
Yeah.

##### **Geohot** [[00:38:30](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2310)]
I mean, what it currently does is it returns whatever is in memory, like, that got allocated.

##### **Chenyu** [[00:38:42](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2322)]
That doesn't sound right. That doesn't make sense at all. The thing you just mentioned also doesn't make sense to me. Why? Like, what dtype that is.

##### **Geohot** [[00:38:50](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2330)]
What dtype do you want?

##### **Chenyu** [[00:38:52](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2332)]
Same as the thing you're adding, though. We don't have dtype-invalid.

##### **Geohot** [[00:38:57](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2337)]
It's not dtype-index. The invalid can be on float. That's fine. The const flow works except with invalid. Yeah.

##### **Chrism** [[00:39:03](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2343)]
When you do this, you have to declare what dtype.

##### **Geohot** [[00:39:06](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2346)]
Like if you do a full invalid, you have to declare the dtype.

##### **Geohot** [[00:39:11](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2351)]
Okay. I don't know. I said I will, whatever.

##### **Geohot** [[00:39:14](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2354)]
No, no, no. But it's actually really important what happens when you try to realize that. So the problem with trying to realize that is: okay, great, it's lowered all the way down and you're left with `const invalid` in your lowered thing. Okay. So if there's ever a `const invalid` left in your lower program, it fails the spec check. Make the error message nice.

##### **Chrism** [[00:39:35](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2375)]
No, no, but what it does is it folds it into the store and then it gates the store.

##### **Geohot** [[00:39:40](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2380)]
So it says like, okay, well, and if you can fold it into the store, that's phenomenal. But if I have invalid plus one, I can't fold that into the store. Invalid plus one is just invalid. Yeah. And I can't store it valid.

##### **Geohot** [[00:39:51](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2391)]
But it gets folded into the store and the store is always invalid. And it turns into a no op. And then you just have a no op kernel. So I'm going to show you, we should probably raise for it. No op kernel. That seems to be the point.

##### **Geohot** [[00:40:08](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2408)]
No, I wouldn't raise for a no op kernel, but I see what you're saying. So you have a rule that takes invalid plus one and just removes the plus one.

##### **Geohot** [[00:40:14](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2414)]
Yeah.

##### **Geohot** [[00:40:17](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2417)]
It's like NaN, whatever, a rule. Yeah. Okay. So for the thing you asked, that behavior kind of seems okay then.

##### **Geohot** [[00:40:27](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2427)]
But we don't know. Yeah. I just don't know.

##### **Chenyu** [[00:40:35](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2435)]
Yeah. I'm just going to try. Yeah.

##### **Geohot** [[00:40:41](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2441)]
Let's, you know, if it seems absurd. I mean, like, I'm, I don't know.

##### **Geohot** [[00:40:43](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2443)]
I don't know. If we introduce invalid, it has all these phenomenal footguns that we'll clean up at the end. `invalid * 0` is undefined. It may be 0 or it may be invalid. Sorry, don't multiply things by 0. Another good answer would be to say that it is invalid.

##### **Geohot** [[00:41:09](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2469)]
No. It may be invalid. It's undefined. Which is what invalid means.

##### **Chenyu** [[00:41:16](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2476)]
No, no, no. Undefined means it can be anything.

##### **Geohot** [[00:41:19](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2479)]
Yeah. It can be 42. 1 plus invalid is always invalid. Invalid times 0 may be 0. Sometimes.

##### **Geohot** [[00:41:28](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2488)]
Invalid can sometimes be 0. I don't know.

##### **Geohot** [[00:41:30](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2490)]
No, no, no. Invalid is invalid. Anyway. It's undefined. It's like dividing by 0 and C. When you divide by 0 and C, sometimes you get an exception, sometimes you don't.

##### **Chrism** [[00:41:43](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2503)]
Okay.

##### **Geohot** [[00:41:44](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2504)]
Yeah, okay. No, I'm fine with it doing that. As long as there's a good justification for why, I don't think we should raise on no-op kernels. I think that the user can shoot themselves in the foot if they use invalid.

##### **Nimlgen** [[00:41:55](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2515)]
Okay.

##### **Geohot** [[00:41:56](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2516)]
So, is it sparingly? Sparingly and carefully.

##### **Chrism** [[00:42:03](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2523)]
Yeah, I mean, the question is whether there's ever another use case for this other than this weird pad situation. I'm sure we'll find one.

##### **Chenyu** [[00:42:10](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2530)]
Well, once you ask something, people are going to find different ways to use it.

##### **Geohot** [[00:42:14](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2534)]
Who knows? But all the research is over there too right now.

##### **Geohot** [[00:42:20](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2540)]
Any thoughts?

##### **Chrism** [[00:42:23](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2543)]
I think, I guess I should also talk about why... The USB GPU stuff is slow. It is true that partially this is slow because of the C-type structure packing. We could speed it up by using struct.pack. When Armand posted that issue, he had an AI-generated patch. Super complicated. There's a much simpler way to do it. But it's still kind of like a fast path for simple C data. So...

##### **Geohot** [[00:42:55](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2575)]
I don't want a fast path.

##### **Chrism** [[00:42:56](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2576)]
Okay.

##### **Chenyu** [[00:42:58](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2578)]
Would you say if we want to revert or no? Are they happy with the speed?

##### **Chrism** [[00:43:02](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2582)]
I think they're not happy with the speed.

##### **Chenyu** [[00:43:05](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2585)]
And will reverting this make them happy about the speed?

##### **Chrism** [[00:43:09](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2589)]
Okay, I'm going to benchmark it and see exactly. But the benchmark that Armand posted that issue did not seem significantly faster. It seems like a bigger issue. And the other thing is that we spent a ton of time in memory.py in the alloc. I'm not totally familiar with what all that code is doing. But it seems to be messing about with tables a lot. And I'm not sure... Anyway, I would have to read this a lot more to understand what exactly is going on. But I don't know if all of that is necessary.

##### **Geohot** [[00:43:41](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2621)]
It certainly seems like we're doing a lot of virtual memory allocation. It's working, but we're doing a lot of virtual memory allocation. So I think probably a better way forward is making sure...

##### **Chenyu** [[00:44:08](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2648)]
It seems to be important. So make sure someone is always on top of it. Either we get a concrete number for what would make them happy, if it's below a certain number.

##### **Chrism** [[00:44:21](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2661)]
Yeah, yeah, yeah.

##### **Chenyu** [[00:44:23](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2663)]
Then we'll decide what we do.

##### **Chrism** [[00:44:25](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2665)]
I'll bug Armand about that and see what he has to say about what performance targets they have. But it sounded like just in general they wanted it to be faster.

##### **Geohot** [[00:44:37](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2677)]
Everyone wants everything to be faster. Okay. Sounds great. Yep. Next spec. There's a link to that spec. Yeah.

##### **Geohot** [[00:44:53](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2693)]
So I linked the spec. It's 80% of what's in TinyGrad right now. I think we're getting to a point where there's a lot of things that aren't really going to change. There's a few things where the simplification path is pretty clear, notably dtype's vec. Dtype's vec shouldn't be a thing. It should just be shape. Why is it not a shape? It should just be a shape. The call was added pretty successfully. I think there were no real regressions or issues. I think call was a strict win. Call is really important. I wish I'd gone with call sooner. There's an algorithmic complexity difference between... I mean, I always knew this with things like nested stuff, but the answer to that wasn't range, it was call. Call is just a much easier thing to do than range. For example, if you have an LLM that has the same layer a hundred times, right? Let's say you have a hundred UOps in a hundred layers. If I spell those all out, if I have a full graph, that's a hundred times a hundred. If I have call, it's a hundred plus a hundred. And we always want to be getting those pluses instead of those times. That's a core philosophical thing of TinyGrad, right? Dtypes are plus. UOps are plus. They're not times. But then UOps themselves were times. So everything's going to be plus with call. So everyone should read over this spec. If you're surprised by any of it, let me know, post about it. There shouldn't be anything surprising. It's not radical. The other difference in the spec from what's actually in TinyGrad is the way that multi is done. So currently when you allocate a buffer on multiple devices, it's not really clear where the multiple devices are. We have these other custom UOps to access them, `MSELECT`, `MSTACK`, and `MULTI`. But we can get rid of `MSELECT`, `MSTACK`, and `MULTI` if we instead make the multi explicitly part of the shape. And what that means is that when you create a buffer on multiple devices, if you create a buffer of size 100 on four devices, it puts 25 on each device and concatenates them. So a buffer is created with a sharding of axis zero, and then you do something special to get a sharding of axis none, because none is the strange case and zero is the common case. Think about memory in general. When I allocate a tensor that's four by 25, that's allocating four chunks of 25 all concatenated. And now when I allocate a multi-device buffer, it's four chunks of 25, it just happens to be across devices. I think that works. I went through and derived all the primitives with it. So yeah, those are the two changes. They'll slowly make their way into TinyGrad. Hopefully everyone sees with call what JIT 2.0 looks like. I should include some stuff about the JIT in here too. It still needs work, but I find that if I spend time in the spec, it takes time away from crashing in the implementation. The other interesting thing added to call is tuple and get tuple. So those aren't in there yet. But they're an exact copy of what's in XLA. And they allow call to return multiple things.

##### **Geohot** [[00:48:37](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2917)]
You can return a tuple from call and then call get tuple on the output of call and retrieve these. Yeah, that's the spec. I'll work on it this week, but a lot of my energy has gone to the raise. The op count there in the core spec

##### **Geohot** [[00:49:00](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2940)]
is 40. If you don't include the codegen ops, and obviously exclude decomposed ops, that's 40.

##### **Chenyu** [[00:49:13](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2953)]
Great.

##### **Geohot** [[00:49:32](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2972)]
This is my stuff.

##### **Chenyu** [[00:49:48](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=2988)]
I will fix any ongoing item-assign issues. There are still two that I'm aware of, but I'm deciding how to fix them. But otherwise, things should be expected to work. This past week I mostly worked on the div and mod stuff. Now it's in a single file. My strategy: there are some discrepancies between how we simplify div and how we simplify mod, and we don't really want that, because we have later rules that try to recombine a div and mod together. So if in earlier steps you treat them differently, then it's a lot more difficult to recombine them later. I already fixed several of the discrepancies. And OpenPilot with image2 is now about 7% faster. Damn, we made something faster.

##### **Geohot** [[00:50:38](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=3038)]
We made something faster. TinyGrad doesn't always get slower. Then you made something faster.

##### **Nimlgen** [[00:50:44](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=3044)]
So.

##### **Chenyu** [[00:50:46](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=3046)]
My strategy here is trying to make the most robust and powerful div and mod to fix all the known issues, then find a way to combine and eventually make

##### **Geohot** [[00:50:58](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=3058)]
it smaller for that file. That's the div and mod. Two questions about this. So do we want to keep both div and mod? I think we do.

##### **Chenyu** [[00:51:26](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=3086)]
So we want to keep both div and mod as ops. I think it's similar to `where` and `max`. It just has much nicer properties to not always infer that from, even if you could.

##### **Geohot** [[00:51:46](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=3106)]
I looked at Luminal. They claim they only have mod, but that doesn't include their shape tracker map, where they actually have both div and cdiv.

##### **Chenyu** [[00:51:57](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=3117)]
That's not... Oh, I also briefly looked into it: we currently have a very annoying correct div mod.

##### **Geohot** [[00:52:07](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=3127)]
What about correct div mod? What about that flag?

##### **Chenyu** [[00:52:10](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=3130)]
Oh, I have a way to do that, but that's really not necessary after we remove image 2 optimization. So for now it's there. I know how to fix it, but...

##### **Geohot** [[00:52:28](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=3148)]
Image one is gone this sprint. Image two is gone this sprint.

##### **Chenyu** [[00:52:31](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=3151)]
Let's go. All right, finally. All right. Got to be on the sprint. So I'm on top of that. I'm aware of that. We will see. Yeah. So I think similar to we keep max, because max has nicer properties. It really makes the code simpler. If you don't want to support one of it at the end of your program, then you can just replace it at the very end.

##### **Geohot** [[00:52:56](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=3176)]
Yeah, the question, yeah. At the very end, all this stuff's easy. The question is for simplification.

##### **Chenyu** [[00:53:00](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=3180)]
Yeah. So for simplification, it's definitely easier to do math and reason about it if we have two. So we definitely don't want div and cdiv, and mod and cmod. Let's just pick one and always use that.

##### **Geohot** [[00:53:16](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=3196)]
Yeah, yeah, yeah. It comes down to whatever is easier to reason about. I think adding something like sub would make things harder to reason about, so we don't add sub.

##### **Geohot** [[00:53:26](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=3206)]
We have mul minus one. Yeah, but that's a lot easier to reason about than sub, right?

##### **Geohot** [[00:53:36](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=3216)]
Also, always keep in mind if you want egraphs, we can add egraphs.

##### **Chenyu** [[00:53:41](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=3221)]
I don't see why egraphs will help, but sure.

##### **Geohot** [[00:53:43](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=3223)]
Well. So OK, so right now we added another. There's two graph rewrite engines now. The other one is very simple. They're the same two that are in MLIR. One of them is a greedy replacement, and one of them is called walk. And walk just tries to replace everything in the graph once. It doesn't iterate and change things, so on and so forth. It's actually really useful for things like substitute.

##### **Chenyu** [[00:54:05](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=3245)]
It's very useful for assign, because otherwise you got the infinite chain.

##### **Geohot** [[00:54:10](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=3250)]
Yeah, yeah, yeah, yeah. No, you get these infinite loops, then you break the infinite loops with tags, then you have to pass or remove the tags. But yes, keep in mind: if you want egraphs, I would rather have two rules on egraphs than 10 rules on not egraphs. It's what I always talk about, how there were two magic rules

##### **Geohot** [[00:54:29](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=3269)]
for all of symbolic. If only we had egraphs. So I don't know if that's true.

##### **Chenyu** [[00:54:35](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=3275)]
So let's... probably at some point we will want that, but not in div and mod. For now, we have a lot of rules that change the order of an add chain to do something. So maybe things like that already have, like, 10 different rules everywhere.

##### **Geohot** [[00:54:56](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=3296)]
Yeah. So to make clear what egraphs are is, like, what egraphs will do is they will try your, you can have rewrite rules. You can have, like, one rewrite rule that factorizes and one rewrite rule that unfactorizes. And then egraphs will run for some fixed amount. So you can have a set of steps. They can also run to convergence. Like, there is a convergence when you don't get any new graphs. And then think about the hypergraph of all the possible graphs. And then you can extract with some limited amount of cost functions on graph. And you can do this data structure efficiently where you, instead of needing to represent all of the graphs, you can represent them as a.

##### **Geohot** [[00:55:39](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=3339)]
I think for the use case, though, that we're seeing, it's probably fine for now. Yeah, I see how that would be a bit different. Okay, maybe that works if you only have one and not something else, because then you can think of all of that. I don't know. I think people want to do that, and then you look at their shape tracker, and they have div and cdiv.

##### **Qazalin** [[00:56:32](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=3392)]
Right. OK. I'm on top of it. The last thing he said was that asm gemm doesn't pass.

##### **Geohot** [[00:56:49](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=3409)]
Great. Yeah, just poke him again. I think it's close. I think when he fixes asm gemm

##### **Geohot** [[00:56:55](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=3415)]
we can merge that. Alright. RDNA5? Oh, RDNA5. Alright, we got a minute to read this Moore's Law Is Dead-branded thing. What is this supposed to... It's GDDR7

##### **Geohot** [[00:57:24](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=3444)]
and it has a memory bus width of 512. Great. Love that.

##### **Geohot** [[00:57:31](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=3451)]
It's supposed to have a... Is this real?

##### **Geohot** [[00:57:37](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=3457)]
I mean, I'm not really referencing any specs. My assumption is just kind of like...

##### **Geohot** [[00:57:45](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=3465)]
Thermal passive? For some reason their big chip is passively cooled? Oh, it's made by MLID. It's not real. Wait, no, it's very likely that their big chip is passively cooled, no? Wait, what? If it's an OCP socket? If it's OCP? You think it's OCP? Oh, you're right. Yeah, if it's like an OEM socket. What is this thing for the market segment? I see. It's not segmented for desktop gaming. Yeah. I see. Interesting. Okay, so that's why it's passively cooled. I don't know. All right, I guess we get the one with 384 then. I guess the problem with that is that the VRAM size is too low if it's OEM. Oh, is that what they're calling frame buffer? I'm assuming.

##### **Geohot** [[00:59:20](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=3560)]
Oh, I see. Okay, cool. So they're making a 72 GB card. I don't know. I mean, maybe the... I don't mind if it's OEM if it's cheap. Wait, why do you think it has to be OEM and it can't be a card?

##### **Geohot** [[00:59:33](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=3573)]
If it's passive, no?

##### **Geohot** [[00:59:36](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=3576)]
No, I agree that, yeah.

##### **Chenyu** [[00:59:38](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=3578)]
I mean, that's just what I go to immediately.

##### **Geohot** [[00:59:41](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=3581)]
Yeah, yeah, yeah. I mean, you're right. If it's passive, it's got to be something. But I don't know. They have this other option with 72 GB of RAM. I think it all works out.

##### **Geohot** [[00:59:51](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=3591)]
AMD knows what they have to make. I mean, look, even if it's just 36 GB, it's kind of small. Hopefully they don't price gouge on the AI/ML version. Yeah. 72 GB is fine. We just might need to build eight-card computers. Hopefully it's not going to be super expensive. Yeah, I mean... Yeah. Okay, cool.

##### **Chenyu** [[01:00:30](https://www.youtube.com/watch?v=SQAUM4KsHmc&t=3630)]
That's it for this meeting. Thank you, everyone. See you next week, same time. Bye bye. Thanks, bye.
