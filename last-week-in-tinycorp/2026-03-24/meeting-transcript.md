# 2026-03-24 Meeting

### Meeting Agenda

**Time:** new meeting #12, 3/23 9pm Monday San Diego time
- company update, new red box?
- IMAGE=2 removal
- AMD flash attention
- broadcast mixin, more Tensor cleanups
- llama training, flat llama
- REMOTE, new jit and mem planner
- viz, SQTT
- other issues, bounties, any karma complaints

### Audio

[Youtube Link](https://www.youtube.com/watch?v=7rTl4VVHDdI)

### Highlights

- **[Company update and box sales](#geohot-000124)**: The team sold a normal red box and has two green box orders in progress, but is being cautious on inventory because RAM jumped from about $90 to $640 per stick.
- **[RDNA 5 optimism and AMD relationship](#geohot-000259)**: Geohot said he is very excited for RDNA 5, expects it to be the generation where AMD is broadly seen as caught up to NVIDIA, and noted a conference-speaking deal tied to an extended AMD contract.
- **[IMAGE=2 removal mostly helped performance](#chrism-000359)**: Removing image tier/image=2 sped up driving vision and driving policy overall, though driver monitoring regressed somewhat and still needs investigation.
- **[IR3 / Mesa image path is working](#chrism-000446)**: Chrism got the image work running with IR3 (Mesa), with only a very small slowdown in driving vision, making the open-source path look attractive.
- **[Mac image-shape mismatch needs a special-case fix](#geohot-000927)**: The team concluded Mac’s image-shape requirements differ from Qualcomm’s, so restoring prior behavior likely needs an explicit conditional in tensor code rather than forcing one shared shape.
- **[Target configuration should be redesigned around user stories](#geohot-001114)**: Instead of a single simplistic target environment variable, Geohot wants the team to model targets around where memory lives and which renderer uses it, then back-solve the right semantics from real use cases.
- **[AMD flash attention is beating Torch on Strix Halo](#geohot-001243)**: Geohot reported a flexible AMD flash attention implementation that beats Torch with its special Triton flash-attention flag enabled, by about 1.8× on Strix Halo.
- **[Single-user AMD LLM serving is still too slow](#geohot-001503)**: After testing AMD’s recommended VLLM and SGLang setups, Geohot said SGLang did not work and VLLM only reached around 35 tokens/sec, far below what he thinks a good single-user experience should be.
- **[Tinygrad should become fully programmable at the UOp layer](#geohot-002029)**: Geohot argued that broadcasting and other conveniences should move down into UOp so tensor and UOp APIs converge, with tensor mainly adding mutability.
- **[Online softmax / Winograd should be graph rewrites, not kernel opts](#geohot-002331)**: The meeting distinguished transformations like online softmax and Winograd from normal kernel optimization, arguing they should live as higher-level graph rewrites instead.
- **[LLM-generated heuristics may replace generic beam tuning](#geohot-002419)**: Geohot proposed using LLM-generated decision trees to encode hardware-specific kernel heuristics, possibly with small search budgets, instead of relying on a universally good beam strategy.
- **[Flat LLaMA training works, but FP32 master weights are required](#geohot-003130)**: Flat LLaMA is integrated and training with standard backward, but convergence currently requires FP32 master weights and FP32 optimizer state because bf16-only updates lose too much precision.
- **[Remote is merged, and JIT should be split into clearer pieces](#chenyu-003726)**: The new remote path is merged, and Geohot wants the JIT refactored by separating out the memory planner and graph pieces so kernel capture becomes the cleaner core.
- **[SQTT / viz tooling is becoming a major optimization aid](#geohot-004330)**: The team praised new visualization links between execs and dispatches, discussed interpreting cycle-like instruction numbers, and framed the goal as enabling humans and LLMs to find fast GEMMs quickly with the tooling.

### Transcript
##### **Geohot** [[00:00:01](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1)]
New Redbox? I don't know anything about that. Oh, so you just say that? I don't think so. What would be new about it?

##### **Chenyu** [[00:00:13](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=13)]
Oh, I thought that's for the MI355 box?

##### **Geohot** [[00:00:17](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=17)]
Oh, that! I mean, yeah, I wonder, like, people are excited about those GB300 NVIDIA boxes.

##### **Geohot** [[00:00:30](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=30)]
I wonder if we...

##### **Geohot** [[00:00:33](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=33)]
Yeah, like, I don't know. I mean, so yeah, I did the math. It's like, you're paying like 80% more for similar specs with half the power draw and better connectivity.

##### **Chenyu** [[00:00:46](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=46)]
You can write CUDA.

##### **Geohot** [[00:00:49](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=49)]
Well, yeah, CUDA is worth something. So I guess, yeah, that's true. I don't know. Okay. Okay.

##### **Chenyu** [[00:01:02](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=62)]
Start with company updates. Any other updates?

##### **Geohot** [[00:01:05](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=65)]
Yeah, so Tiny with two eyes. You guys see the BoJack Horseman episode where they have Disneyland with two eyes? There's literally a BoJack about this. They probably stole it from them. Yeah, so we're suing them for trademark infringement. But only after they make money. So my plan is to wait for them to make money and then sue them and then take the money. So if any of this makes it back to Tiny, I'm going to sue them. Okay. Tiny with two eyes. Hope you don't, you know, hope you don't spend it too fast.

##### **Chenyu** [[00:01:36](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=96)]
Three by one?

##### **Geohot** [[00:01:37](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=97)]
A Tiny? No, it's a total scam.

##### **Chenyu** [[00:01:40](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=100)]
Okay.

##### **Geohot** [[00:01:41](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=101)]
It's a total scam. They're... Okay. Have you seen, like, every once in a while, these things hit Hacker News where someone will get like, I got Kimmy K2.5 to run on my iPhone. It gets .01 tokens per... It did a token. It took a minute.

##### **Chenyu** [[00:02:02](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=122)]
Yeah, just use your disk.

##### **Geohot** [[00:02:04](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=124)]
Use your disk. Yeah, exactly. So that's pretty much what this scam is. You know, the thing has no memory bandwidth. Yeah. Let's see. We sold a normal red box. We have two orders for green boxes. They haven't converted yet. With a whole Hacker News thread. Tiny is spending a lot of money on advertising. So it's really just all going to flow into our pockets, too. So you know what? We're going to sell it. We're winning on a lot of fronts, you know? They spend money. We take their money. Big win. Yeah, we got two orders for green boxes. I'm trying to not order too many green boxes. RAM is up to $640 a stick. The RAM that we were paying, $90.

##### **Geohot** [[00:02:50](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=170)]
We do not want to get stuck holding the bag.

##### **Qazalin** [[00:02:56](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=176)]
Okay.

##### **Geohot** [[00:02:59](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=179)]
Okay. Okay.

##### **Geohot** [[00:02:59](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=179)]
So I'm very excited for the RDNA 5.

##### **Geohot** [[00:03:03](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=183)]
I think RDNA 5 is going to be the generation where everyone accepts that AMD caught up to Nvidia. Great. Looking forward to that. I get a special deal when it's out.

##### **Geohot** [[00:03:26](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=206)]
Well, I'm going to speak it there. I offered. I agreed to speak at their conference. They agreed to extend our contract. I agreed to speak at the conference. Everybody wins. It's a win-win cooperation partnership. So we'll see if that extends to good prices on RDNA 5.

##### **Geohot** [[00:03:44](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=224)]
Sounds good to me.

##### **Qazalin** [[00:03:46](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=226)]
Okay.

##### **Geohot** [[00:03:49](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=229)]
That's it? That's it.

##### **Qazalin** [[00:03:53](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=233)]
Okay.

##### **Geohot** [[00:03:54](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=234)]
Cool.

##### **Chenyu** [[00:03:56](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=236)]
Next story was image tier removal.

##### **Chrism** [[00:03:59](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=239)]
Yeah. Image tier was gone. Yeah. I'm happy about that. It made driving vision and driving policy faster, although driver monitoring was a bit slower. So we need to look into what exactly is going on with that. But mostly seems like a win. Still needs to be moved to later in code gen. Just to totally isolate that whole optimization. But I was looking into doing that. Seems doable.

##### **Geohot** [[00:04:39](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=279)]
Yeah. Pretty good. What else?

##### **Chrism** [[00:04:46](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=286)]
I looked into a little bit into getting it to work with IR3. Some like latent bug in the way that we were handling textures for IR3. So it also works. And we also get good performance there. It's like marginally worse. It's like a couple fractions of a millisecond slower in driving vision.

##### **Geohot** [[00:05:07](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=307)]
So IR3 is the Mesa.

##### **Chrism** [[00:05:09](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=309)]
Yeah.

##### **Geohot** [[00:05:10](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=310)]
And it works. It does.

##### **Chrism** [[00:05:11](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=311)]
Cool.

##### **Qazalin** [[00:05:12](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=312)]
Yeah.

##### **Chrism** [[00:05:14](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=314)]
A couple milliseconds slower. That's a lot slower. No, fractions. Like 10 something milliseconds. I guess like 0.2 milliseconds.

##### **Geohot** [[00:05:20](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=320)]
That's almost worth it just for open source.

##### **Qazalin** [[00:05:22](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=322)]
Yeah.

##### **Chrism** [[00:05:24](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=324)]
Anyway, I don't know. I thought I might throw that into the chat. I think it's a benchmark so it doesn't have a latent bug in it.

##### **Geohot** [[00:05:31](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=331)]
I mean, if the speed is comparable, I'd much rather use Mesa than the closed source one.

##### **Chrism** [[00:05:36](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=336)]
Yeah.

##### **Geohot** [[00:05:38](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=338)]
So anyway. Do you have the LLVM running in the? Yeah.

##### **Chrism** [[00:05:43](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=343)]
Yeah.

##### **Geohot** [[00:05:46](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=346)]
I'm curious what the LLVM looks like and how much we're going to have stuff and stuff.

##### **Chrism** [[00:05:49](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=349)]
It looked pretty normal.

##### **Geohot** [[00:05:52](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=352)]
How are they doing images?

##### **Chrism** [[00:05:53](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=353)]
So they have it call a function called like. Yeah. Two column read image or something like that.

##### **Geohot** [[00:05:59](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=359)]
Yeah. So we can just maybe can we just implement two column read image and like three lines? Yeah.

##### **Chrism** [[00:06:04](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=364)]
Yeah. So I got to try that out. But I'm not sure it just work. I mean, I haven't tried it like every small edge case. Like I don't know. Maybe when I call sign, it does some like weird thing. But like it's like it's probably fine.

##### **Chenyu** [[00:06:18](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=378)]
I have a small thing for image. So for now, because if I try to run the comment, we have a little bit of a problem. I have that comment that checks how many image reads are there with the loud image reading. If I just run that comment on Mac will fail because Mac picks a different value or filtering and that's slightly annoying for development. Can you do something about that?

##### **Chrism** [[00:06:46](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=406)]
Yeah. So I mean, the issue here is that the image shape requirements are different on Mac than they are on.

##### **Chenyu** [[00:06:59](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=419)]
But if we use the same as the Qualcomm one, is it just like fail to compile or slow? Yeah.

##### **Chrism** [[00:07:07](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=427)]
Yeah. It'll fail to compile. Like you cannot create images that are the like the requirements for the image shapes are different.

##### **Geohot** [[00:07:15](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=435)]
Well, if it fails to compile, it should just not use image.

##### **Chrism** [[00:07:19](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=439)]
Oh, yeah. But if I if I were to try and tell it to use the same shape. It's not that it will compile, it would fail to run because we create images on the fly and that's not a valid image shape.

##### **Geohot** [[00:07:31](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=451)]
Yeah, there's like certain strides that are just enforced by the hardware and the texture

##### **Geohot** [[00:07:35](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=455)]
sampler. They're different. I see.

##### **Chenyu** [[00:07:44](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=464)]
Yeah. I mean, you can see that way. This is annoying. I don't know. Yeah, it definitely is. Can this work with the null backend? Is there a way? I just I just want to be able to understand that. I just want to run this locally on a Mac and see how many MI like regressed the imagery.

##### **Chrism** [[00:08:01](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=481)]
Yeah. Um, let me think about that. So maybe the null backend with IR3, we could find a way to get the number of image reads through IR3. The Mesa stuff because

##### **Geohot** [[00:08:15](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=495)]
Why do you need a renderer in order to get the number of image reads? The null backend? Uh, yeah. Yeah, I guess that's true. You shouldn't need a renderer. Yeah. If you're just looking for the number of imagery, that should work with null. Yeah. Uh, yeah. Yeah. Well, we should have a different way of counting it.

##### **Chrism** [[00:08:39](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=519)]
Yeah.

##### **Chenyu** [[00:08:40](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=520)]
That should be fine. Okay. Anyway, that was my small, small thing because I can no longer run the same thing on Mac.

##### **Chrism** [[00:08:48](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=528)]
Yeah, I know. I get it.

##### **Geohot** [[00:08:50](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=530)]
Wait, could you ever run the same thing on Mac?

##### **Chenyu** [[00:08:53](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=533)]
What do you mean? I always develop. Yeah. I was doing this previously on Mac.

##### **Geohot** [[00:08:57](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=537)]
What's changed? Mac always had this limitation. The sizes were always different.

##### **Chrism** [[00:09:03](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=543)]
I it's that it would. Well, yeah, actually, this probably never worked with image one.

##### **Chenyu** [[00:09:08](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=548)]
Yeah, I mean,

##### **Chrism** [[00:09:09](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=549)]
It may have worked with image two.

##### **Chenyu** [[00:09:10](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=550)]
But how did it work with image three? Previously with image two, it worked, right?

##### **Geohot** [[00:09:13](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=553)]
Because it just pads the pitch. I can't just just pad the pitch. I don't understand why it regressed. Right? Like whatever shit the hardware had to do was still true. That's true. Yeah.

##### **Chrism** [[00:09:25](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=565)]
Yeah. No, I just fix it.

##### **Geohot** [[00:09:27](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=567)]
All right. So you're saying like what you need an F statement tensor to say if it's Mac do this. Yeah. Yeah.

##### **Qazalin** [[00:09:34](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=574)]
Okay.

##### **Chrism** [[00:09:35](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=575)]
I don't know. I think knowing, but I can just do that.

##### **Geohot** [[00:09:38](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=578)]
That seems like the right place to put it.

##### **Chrism** [[00:09:40](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=580)]
Okay. Okay.

##### **Geohot** [[00:09:40](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=580)]
Yeah.

##### **Chrism** [[00:09:42](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=582)]
Yeah. That also makes it.

##### **Geohot** [[00:09:43](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=583)]
No, we're going to restore. If there's any regressions from the image equals to behavior, there shouldn't be. The only problem is that the shapes are actually internally slightly different. Pat.

##### **Chenyu** [[00:09:54](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=594)]
Yeah. So if we can just, even if it's the debug flag, I think that would be helpful. Let's just understand.

##### **Chrism** [[00:10:02](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=602)]
I can just, I can just restore the same behavior, but with a statement and a. Okay.

##### **Geohot** [[00:10:07](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=607)]
Sure.

##### **Chenyu** [[00:10:10](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=610)]
Yeah. Because obviously our goal is whatever we put on the CI and whatever, which machine we pick, if we can run that issue past.

##### **Qazalin** [[00:10:19](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=619)]
So.

##### **Geohot** [[00:10:22](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=622)]
Yeah. Okay. Cool. Anything for the target triple thing?

##### **Chrism** [[00:10:30](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=630)]
Yeah. Just trying to think about like the, the problem with having it being an environment variable, like target is in the case where you have, for instance, like multiple devices that you're saying, for instance, like I'm going to run something on the Qualcomm GPU, but then I'm also going to run something on my AMD GPU that's plugged in over USB. And how do you specify that? Like, oh, I've got a, I've got a, I've got a, I've got a, I've got a, I've got a, I've got a, I've got a, I've got a, I've got a, I've got a, I've got a, I've got a, I've got I want to use a DLL. But I want to use Qualcomm IR3. That's the one, I think maybe a little bit tricky case. And then also like, there's always just a little bit of weirdness around how you're going to use null. But I think that's, that's resolvable.

##### **Geohot** [[00:11:14](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=674)]
Oh, I think the answer to that is targets. Right. And then you have your, did you write this user story somewhere? Yeah. Okay. We'll go through the math. I think the idea is basically you have the place the memory lives, the renderer, and the renderer arts. Memory, renderer, renderer arts. You can associate different memories with different renderers. We can figure out also if we want to be able to do some things with one renderer and some things with another renderer. There should be able to be a context bar for that.

##### **Geohot** [[00:11:53](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=713)]
Yeah. I'd say that you have one environment variable, like targets,

##### **Chrism** [[00:12:00](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=720)]
and then it's like a separator or something like this.

##### **Geohot** [[00:12:03](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=723)]
Maybe. I don't know. We have to go through that.

##### **Geohot** [[00:12:06](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=726)]
We're going to go through the user stories and then back solve for what the semantics should be.

##### **Chenyu** [[00:12:13](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=733)]
I think we already know there are some places, some existing stuff we're going to remove, and there are some things we want to do but currently are very hard to do. And then just combine that. I think it's fine not to get this right in the first time, but every incremental change benefits the users.

##### **Qazalin** [[00:12:31](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=751)]
Yeah.

##### **Geohot** [[00:12:34](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=754)]
Anything else? Let's see. I think. Yeah.

##### **Chenyu** [[00:12:40](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=760)]
Move on to George's stuff.

##### **Geohot** [[00:12:43](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=763)]
I mean, there's a change I want to think about there, which is like when you have the AMD device, it's just all the GPUs. It shouldn't be like... you can't select AMD 0, AMD 1, but let me figure that out. That's another question, right? You have the memory, and then like you split out the memory. And we don't split out the memory for the CUs, so why should we split out the memory for the GPUs? Then there are also compute devices. So anyway, my stuff. Yeah, I wrote on the board for a bit. It's like, right, flash attention with the new stuff. So we're pretty flexible on AMD flash attention that outperforms Torch. And it doesn't just outperform baseline Torch. It outperforms Torch with the secret flag. So baseline Torch is terrible. Baseline Torch isn't flash attention. If you want flash attention, you have to put the special Triton enable flag, and then even with that we're beating it by 1.8x on Strix Halo. And that's still also pretty unoptimized. I did have to write the warp shuffle thing. Yeah. I mean, a lot of the writing, but the LLMs are quite good at using our API too. They're a lot better at using our API than they are at writing assembly, which is good. I think there's just a lot more cleanups there. I'm figuring out how to remove ranges. I fixed a bunch of bugs in indexing, fixed a bunch of bugs in the emulator. They're just kind of moving toward having a set of kernels for AMD, really for Strix Halo, that are fast. I'm real excited about the Qwen 3.5 thing. Yeah. I mean, if we can be the place where you just `pip install tinygrad`, and then it runs Strix Halo, and then it runs Qwen 3.5 fast on your Strix Halo, that's pretty good. I think we can get a lot of users with that, or some users with that. Also, I spent the morning playing with `vLLM` and `SGLang`, and I tried it really the best way I could. I didn't mess around. I tried the AMD Docker the exact way all the docs say to. `SGLang` doesn't work. `vLLM` gets about 35 tokens per second single-user.

##### **Geohot** [[00:15:03](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=903)]
Terrible. All of these, the theoretical is 2000.

##### **Geohot** [[00:15:12](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=912)]
Fine, fine, you're not going to hit the theoretical, but can I at least have 200? I think there's a real... there's a lack of high-speed single-user LLM runners, which is kind of what you want. Like, what the individual wants, what I want, what would get me to not use Claude? Claude gets me like 40 tokens per second. If I could have Kimmy with 400, I don't know, it might be better. It is cool. It stood up on, I posted on the TinyBox Access channel. If anyone wants to use it, you can just access it from inside our network. It's a `vLLM` server, so you can point your open code at it or whatever. Point your open claw at it. And yeah, I mean, I want that to be like a good experience. I want to have something that we can offer people, starting with people inside the company, hundreds of tokens per second. So yeah, I don't know how we get that yet, but maybe through writing kernels, maybe it will work.

##### **Geohot** [[00:16:29](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=989)]
How well is this testing CI? How will what be testing CI?

##### **Chenyu** [[00:16:36](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=996)]
AMD Flash Attention.

##### **Geohot** [[00:16:38](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=998)]
Oh, it works. Yeah, I can add a CI. The emulator works.

##### **Chenyu** [[00:16:42](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1002)]
Yeah, add something, because I'm working on the broadcast thing, and I just look through your examples, finding the things you probably want.

##### **Geohot** [[00:16:50](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1010)]
Oh, great. Yeah, yeah, yeah. I'll add a CI. I'll make sure both my AMD flash attention and my AMD GEMM.

##### **Chenyu** [[00:17:02](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1022)]
Copy something.

##### **Geohot** [[00:17:05](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1025)]
Copy what?

##### **Chenyu** [[00:17:06](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1026)]
There's one called `amd_copy_matmul` or something.

##### **Geohot** [[00:17:10](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1030)]
Yeah, yeah, yeah. `amd_copy_matmul` is a new one. I think `amd_asm_matmul` should work in the emulator too. So `amd_asm_matmul` is still 80% faster than `amd_copy_matmul`. Yeah. Let's see here. Most of that gap is LLVM issues. It has to do with how LLVM poorly schedules the loads. We have to go to assembly if we want to get that performance.

##### **Geohot** [[00:17:43](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1063)]
I see.

##### **Geohot** [[00:17:45](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1065)]
Yeah. I mean, there's a lot to be gained, just by getting the memory correct. Yeah. And we sort of have this distinction between. Yeah. I'm drawing more of this distinction between the first half of the kernel generation, which is memory, and the second half, which is code gen. I also realized that the expander, the real name for it is derangify. We have rangeify and derangify, and I think we can write much simpler versions that basically now I understand what they are. Yeah, I got to work on...

##### **Chenyu** [[00:18:18](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1098)]
What's derangify?

##### **Geohot** [[00:18:21](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1101)]
Expander is derangify.

##### **Chenyu** [[00:18:23](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1103)]
Then maybe what is rangeify?

##### **Geohot** [[00:18:27](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1107)]
Rangeify, if you have a shape, you have a shaped tensor, rangeify removes shapes from the tensor. There's full rangeify and partial rangeify, but if you do a full rangeify, it removes all the shapes in the tensor and everything basically has no more shape in it, and then it has ranges. A derangify or expander lets you take a range and insert it back into the graph.

##### **Geohot** [[00:18:50](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1130)]
And that's like an upcast.

##### **Geohot** [[00:18:54](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1134)]
You can do this like taking and removing ranges, but the ultimate goal of this stuff, and hopefully what'll be done in maybe like six weeks, is the removal of DType.

##### **Geohot** [[00:19:11](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1151)]
Yeah. Oh, that sounds good. I see why Kimmy's bad. Yeah.

##### **Qazalin** [[00:19:19](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1159)]
Yeah.

##### **Geohot** [[00:19:22](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1162)]
Anyway, anything else? Nope. Okay.

##### **Chenyu** [[00:19:27](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1167)]
My stuff. I was mostly doing cleanups between the tensor and uop. So, a tensor constructor should be a lot cleaner now, a lot of logic that we previously have for index. Now it's called weakint. There's a function called tensor.tensor. But from uop, now we have a single coder that calls that. And I was looking into how to, like what of the broadcast to move to the common mixing, because tensor for now does a lot more than uop. Tensor does the DTYP upcast. So if you add an integer tensor to a float, small float, it will upcast to the common upper DTYP. We don't do that for uop. For uop, you just inherit the type from the uop.

##### **Geohot** [[00:20:24](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1224)]
I think we should.

##### **Chenyu** [[00:20:27](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1227)]
We should do that in uop?

##### **Geohot** [[00:20:29](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1229)]
Yeah. I think we want all the broadcasting in uop. I think that, so we were going over here on some ways, like to talk about what the specification is for functions. And like, coding at the uop layer is a lot nicer than coding at the tensor layer.

##### **Qazalin** [[00:20:48](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1248)]
Okay.

##### **Geohot** [[00:20:49](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1249)]
And we want to bring all of the niceties from tensor into uop. So I don't think there's anything that tensor should do that uop doesn't do, except for things that are stable.

##### **Chenyu** [[00:21:02](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1262)]
Or things like tensor can create a tensor from a uop, right? There's no such thing as uop create a uop from a uop.

##### **Geohot** [[00:21:12](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1272)]
Yeah. Tensor can create a uop from a uop. But even then, I'm not sure. Oh, no.

##### **Chenyu** [[00:21:18](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1278)]
Tensor can create a tensor from a uop.

##### **Geohot** [[00:21:21](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1281)]
Yeah. I don't really understand this. I don't understand why that function exists, a from uop function. Why can't you just like, like a tensor is just a little container around a uop.

##### **Chenyu** [[00:21:31](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1291)]
Because we also use uop in a symbolic shape.

##### **Geohot** [[00:21:37](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1297)]
That's fine. Okay.

##### **Geohot** [[00:21:43](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1303)]
That'd be fine. Basically. I want to make tinygrad completely programmable at the uop layer. The only thing that the tensor layer gets you is mutability.

##### **Geohot** [[00:21:59](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1319)]
Okay. I mean, that makes sense.

##### **Chenyu** [[00:22:01](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1321)]
I will think more about this. But I think generally making the tensor thing, making the things that specific to tensor smolders seems to be the direction we want to go. So. Yeah.

##### **Geohot** [[00:22:16](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1336)]
Like cleaning up that flash attention to remove all the ranges from it basically is when all the ranges are gone and all like the extra reshapes and expands are gone. And we've reached the point where like uops are very programmable. Like we kind of have these two APIs and we're coming at them from both sides. We like unified them, right? Like there's a tensor API from the high level. There's this like uop kernel, like you can use it to code flash attention, but those things should be unified. Yeah. You should be able to basically write flash attention in tensor. And I think that's the answer. I mean, I think the answer, oh, I have two things that I think I now have answers to. One is this, like, how do we auto discover flash attention? How do we auto optimize flash attention? We don't finding that online max is not a transformation that we should ever put in some auto magic shit. Like if you want to do that. Just code by hand. And we should just make the API to code that as simple as possible because that online max is not a, like it changes the computation.

##### **Geohot** [[00:23:31](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1411)]
What about Winograd?

##### **Geohot** [[00:23:34](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1414)]
Winograd. So it's similar. It's similar. Sure. Sure. You want to have Winograd and online max are basically the same thing. Yeah. I mean, you can have these as these like light post-processing layers after tensor. I mean, they can still be graph rewrites. My point is they aren't kernel optimizations. So yeah. I mean, yeah, obviously they can still be like graph rewrites, right? We can have some high level API that then like goes and pulls out things that look like attention and things that look like things that look like, oh, this will benefit from online soft max. This will benefit from kind of in the same place we have split reduce optimal. Yeah. That makes sense. Yeah. So I think, yeah, they can be rewrites, but they're not, they're not opt ops.

##### **Geohot** [[00:24:18](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1458)]
Yeah.

##### **Geohot** [[00:24:19](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1459)]
Yeah. Yeah. Yeah. And then the other thing I realized is we always would talk about some way to do like, okay, so we have beam and beam is slow. What we want is beam to automatically discover heuristics for a system. And I think we have now been given the thing that does this. I imagine heuristics. Yeah. This thing is becoming a big directory, like a couple thousand lines, but it's all LLM generated, and it's all like simple. It's all like it has a very narrow API and a very clear definition of winning. And then when you want to add a new accelerator to tiny grad heuristics, we have some big set of kernels. We tell an LLM, find heuristics that do this stuff. You're welcome to use beam search. I've seen it. You're welcome to use whatever. And then this solves the problem of, how is it just

##### **Geohot** [[00:25:15](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1515)]
fast out of the box? It makes sense. Because I think we'll never be able to build something

##### **Geohot** [[00:25:29](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1529)]
that's generically good. There's so many little bits of subtlety and nuance.

##### **Chenyu** [[00:25:36](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1536)]
We just need to go. It always feels like you need at least a very thin layer of search. It's just you can make that pretty fast. We have more and more stuff look like now in the earlier past. We use different proxies to pick some options.

##### **Geohot** [[00:25:53](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1553)]
Yeah, and like the new heuristics, one of the options can be search. The heuristics the LLM finds can include, we can give it a budget. We can say, you're allowed to run in benchmark three kernels. And then it'll make some big mess. It'll give you less of 1,000 lines of if statements. But who cares? Because the API is really narrow.

##### **Chenyu** [[00:26:16](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1576)]
So it's a decision tree. And it's also easy to read from LLM. Yeah.

##### **Geohot** [[00:26:24](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1584)]
It's an LLM-built Python decision tree.

##### **Chenyu** [[00:26:29](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1589)]
OK. One last thing I was thinking about was the weak int. So I renamed the DTYPES index to weak int. And it will probably work very similar to Jack's weak int. So this is also tied to the type promotion stuff in the broadcast. So I want to think through. This idea is we now have some custom rules saying what this int type should do. And basically, the idea is if you've got a Python int, and you have a tensor, or you are a Python int, and you're acting on that Python int, what DTYPES should that be? Currently, we have two sets of different rules, one for tensor, one for UOP. We might unify them to the single one. But still, the idea there is you can decide the type of any objects from Python. You just need to know if it's a float or if it's an int. And you can decide the concrete actual type in the kernel much later if you keep those as weak int. And for now, if you look at the tensor init function, we pretty much just put default float and default int for them and go from there. You can imagine a word that those are determined later. Yeah, so thinking about that, that will solve some weirdness in terms of int64 plus uint64 becomes a float8. Also, we have a lot of different float8. I also want to think how to unify these better.

##### **Geohot** [[00:28:12](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1692)]
Yes.

##### **Chenyu** [[00:28:13](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1693)]
We previously had some priority thing, but now people just, we have priority 0, minus 1, 800, or whatever. So it would be nice to clean this up.

##### **Geohot** [[00:28:25](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1705)]
I don't know about the priorities, but I certainly know the way the float8 should be unified. So we have those two float8 types. One for NVIDIA and one for AMD, and they are slightly different. I don't think we should track those as different D types. I think that's just something that's done at CodeGenLayer, and we're kind of just indifferent to those things. You have to just kind of know.

##### **Chenyu** [[00:28:51](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1731)]
That's tricky, because that also ties to how you want to use this. If you write a custom kernel and you really said for the forward, I want this one, and for the backward, I want that one, you need to be able to specify that using D types.

##### **Geohot** [[00:29:04](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1744)]
Oh. Yeah. Yeah, absolutely. But there are two real types, and the two real types are FP8 and BF8.

##### **Geohot** [[00:29:13](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1753)]
There's not four. It's probably also more than two.

##### **Geohot** [[00:29:20](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1760)]
I'm pretty sure it's two. Everything pretty much talks about two. There's FP8 and BF8.

##### **Flata** [[00:29:25](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1765)]
Yeah, there's only two.

##### **Chenyu** [[00:29:27](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1767)]
Two on the hardware, or two in the concept? Because people also talk about the one that is 0.

##### **Qazalin** [[00:29:35](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1775)]
Yeah.

##### **Chenyu** [[00:29:36](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1776)]
As far as I know, people only use two.

##### **Geohot** [[00:29:39](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1779)]
Yeah. Yeah. There's the 4-bit exponent one and then the 5-bit exponent one.

##### **Qazalin** [[00:29:43](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1783)]
Yeah.

##### **Geohot** [[00:29:46](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1786)]
How about the 0 exponent one? I haven't seen anyone use this.

##### **Chenyu** [[00:29:53](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1793)]
I thought that's the new thing. No. I don't know. OK, anyway, I think keeping two makes sense. So we'll think about that more. Yeah. It'll be nice. Once this is clean up and back is removed, D type can be small and clean again. That would be really good.

##### **Geohot** [[00:30:13](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1813)]
Yay.

##### **Chenyu** [[00:30:15](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1815)]
OK. Next, LLaMA training. Flat LLaMA.

##### **Geohot** [[00:30:21](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1821)]
So flat LLaMA is integrated. `apply_grad` doesn't train.

##### **Geohot** [[00:30:29](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1829)]
What do you mean `apply_grad` doesn't train? The grad is 0. What grad is 0?

##### **Flata** [[00:30:38](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1838)]
The grad on anything on most of the tensors

##### **Geohot** [[00:30:42](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1842)]
that are not on the immediate output layer is 0. What's apply grad? Are those some bug in my stuff?

##### **Flata** [[00:30:53](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1853)]
Yeah. Your `apply_grad` function that saves memory on the backward.

##### **Geohot** [[00:30:58](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1858)]
Oh. Did you fix it or did you remove it? No. So right now, I'm just training with backward. I don't know if it's working. I just looked at it a bit and then I couldn't fix it. I see. But you are using flat. Yes. I'm using flat LLaMA just with backward. That should be fine. Yeah. We just need to add in that hack and do it properly. Backward should be fine. Just make sure that you're cache hitting by the second time.

##### **Geohot** [[00:31:27](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1887)]
Yeah.

##### **Qazalin** [[00:31:28](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1888)]
OK.

##### **Geohot** [[00:31:30](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1890)]
Also, wait. 7 hours, 41 minutes is the best time we've ever gotten. Really? Yes. I thought we had MFUs that were like over 20. Yeah.

##### **Flata** [[00:31:40](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1900)]
But this is actually lower MFU, but it actually converges in the correct number of steps.

##### **Geohot** [[00:31:46](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1906)]
Very good. And wait, you had to put floats in FP32? Yes. FP32 master weights with FP32 optim is the only way I got this to converge.

##### **Geohot** [[00:32:00](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1920)]
But the weights on the GPU are still 16? Yeah. I think it's still 16. So we cast down for forward. Wait. The weights on the GPU are 32. There's a copy in float and a copy in bfloat16. On the GPU? Yes. We got to fix this. I'm trying Stochastic Rounding as well.

##### **Geohot** [[00:32:30](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1950)]
Yeah. Wait. But how did this get worse? Didn't this used to work? Yes. But we weren't following MLPerf reference in it.

##### **Flata** [[00:32:39](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1959)]
Oh. So now that I've implemented reference in it, because on the output layers, the residual is scaled down so that the residual path stays the same throughout the model.

##### **Geohot** [[00:32:52](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1972)]
And then because that update is now really small, it goes outside of bfloat16 precision. And the model stops training. Can't we just like scale this?

##### **Geohot** [[00:33:06](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1986)]
We could potentially. But as far as I can tell, the way that everyone does the training is FP32 weights. FP32 master weights?

##### **Geohot** [[00:33:18](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=1998)]
Yes. That you run the optimizer on? Yes. Do you need m and v in FP32 as well?

##### **Geohot** [[00:33:30](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2010)]
Yes. I tried without and it also diverged. Oh, I see. Where are we storing those? Also on the GPU right now. For AP, everything fits. AP, everything fits, sure. But wait, is this training done with MP or DP? DP. This is DP.

##### **Geohot** [[00:33:49](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2029)]
Yeah. AP is DP. AP is DP. We should be testing more with MP too.

##### **Flata** [[00:33:55](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2035)]
How much slower? I saw the contract was extended and then saw that we wanted to submit AP for this.

##### **Geohot** [[00:34:01](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2041)]
We want to submit AP, but we need a much better time than this. We need to get AP at least submittable because right now our AP is, there's still some stuff that is missing. What's not submittable about it right now? Just weight init. Oh, so, but this new one was with the right weight init or not with the right weight

##### **Flata** [[00:34:20](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2060)]
init? The new one's with the right weight init. But this new one's submittable? Yeah. Once I add logging. I need to add logging.

##### **Chenyu** [[00:34:29](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2069)]
Log in and add the script so that we should have a one clean script. Like just by repeating running it, we will have a submittable artifact. Yeah. Okay.

##### **Geohot** [[00:34:41](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2081)]
So they got 122 minutes. Can we beat that? You can try.

##### **Geohot** [[00:34:50](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2090)]
So WQKV on 8B hits a very bad gem shape and it's very slow. Did you, we can disable WQKV. Yeah.

##### **Flata** [[00:35:04](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2104)]
I just added a toggle for it and then we can split it.

##### **Geohot** [[00:35:09](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2109)]
Yeah. A hundred. We got to get two hours.

##### **Chenyu** [[00:35:15](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2115)]
I think adding logging and adding something like a benchmark so that people can easily see what's slow helps because then whoever is interested can like improve something.

##### **Geohot** [[00:35:30](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2130)]
Yeah. With the benchmark script, like benchmark equals five or something. Yeah. It's all pretty fast now too, right? Like it boots up real fast, right?

##### **Geohot** [[00:35:37](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2137)]
Yeah. Great. Oh, you're using flat transformer. Did you pass anything on the backwards?

##### **Geohot** [[00:35:46](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2146)]
You're just. So the backwards is okay. So the function, uh, the function. I tried with function and without function. Was this training run with or without function?

##### **Flata** [[00:35:58](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2158)]
This was with function.

##### **Geohot** [[00:36:00](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2160)]
Okay. So is it faster without function? I believe last time I tried it. Yes. So what you want to do is keep function, you want function to return intermediates, and then it'll use those intermediates on the backward pass. You what I mean? I see. Yeah, so currently, if you use function, it will just use only what's returned from the function in the backward pass and recompute everything else. But if you return some intermediate stuff, you're trading off memory for not recomputing, basically. We should have locked the memory.

##### **Geohot** [[00:36:53](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2213)]
And I don't have to use these, I just have to return them. You don't have to use them, yeah, you can just return them. Okay. That should work. If it doesn't work, I'll go into it. But yeah, I should start. Okay.

##### **Chenyu** [[00:37:10](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2230)]
I think it's also nice just post whenever you have a run or have some config in the channel, so you don't need to wait for the weekly meeting to update on this. Yeah.

##### **Geohot** [[00:37:26](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2246)]
Next, the new remote JIT thingy. Yeah, so remote is merged. You need to use the variable `REMOTE_IP_PORT`. For the new JIT, yeah, we use the old one for now.

##### **Qazalin** [[00:37:59](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2279)]
Yeah.

##### **Geohot** [[00:38:01](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2281)]
That was just an error from the build guide. Yeah, that was actually a problem. JIT 2.0, I think we should solve the assign function problem. Yeah, mostly that's the problem.

##### **Geohot** [[00:38:21](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2301)]
We actually have tests already with the wrong behavior, so we should fix this. So I think before we do assign-in-function, we have to remove the graph from the JIT. Yeah, we talked about it. Yeah, we came up with a plan for a new JIT, and you basically get into what the old JIT is. The old JIT is like a memory planner and a graph and a kernel capture, so we can pull out the memory planner and the graph

##### **Geohot** [[00:38:54](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2334)]
and then the kernel capture is just, okay, that's what becomes the functional core. So we can pull out the memory planner and the graph and then we can do the same thing. Yeah, I'll do the next step to the right.

##### **Geohot** [[00:39:08](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2348)]
Yeah, good work on the mem planner. I didn't look. Does viz show it nicely?

##### **Geohot** [[00:39:17](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2357)]
Okay, it does show, but it's pretty laggy. Yeah, let's see what we've got. This is so slow. Why did my computer crash? I crashed my GPU doing this. I don't know. Okay, so it's in schedule. I can find the memory plan. Oh, these are all pointing to a buffer. Oh, cool. Yeah, so there's something you'll see on schedule now. Oh, those are all the same view. What's that doing? Cool. Yeah, that's great. I can work off that. The other thing, talk about GMMU. Oh yeah, because this disables the gaming view that makes use of that.

##### **Geohot** [[00:41:01](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2461)]
I mean, I think it points to even more like tinygrad long term will have the ability to just not have an MMU. MMUs are slow and have TLB misses, and like you only need one if you did a bad job centrally planning.

##### **Geohot** [[00:41:24](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2484)]
Yeah, I'll try your GPU without an MMU today. `GMMU=0`, on both?

##### **Geohot** [[00:41:29](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2489)]
oh

##### **Geohot** [[00:41:30](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2490)]
no

##### **Geohot** [[00:41:31](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2491)]
Works on both, really? And the NVIDIA, like, it boots fine without the MMU? Actually it's like identity mapping.

##### **Geohot** [[00:41:38](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2498)]
oh you didn't have any magic on invented okay

##### **Geohot** [[00:41:44](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2504)]
basically actually uh the biggest limitation is that you need to access both um like you need to specify your access like if it's cached or not

##### **Geohot** [[00:41:57](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2517)]
and the only way you can do this is with page tables what's the default i mean you can set this no no no no but what if i turn the mmu up what's the default

##### **Geohot** [[00:42:10](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2530)]
so we have identity maps nah what if i turn the mmu up is it cached no you can choose i mean on amd you can choose on amd it's on cache if it's cache coherent if it's not on amd you can choose at what level like the instruction chooses right no in the page globally oh globally no you can choose globally like for the whole like the aperture the whole okay for the aperture that makes sense and then what about for nvidia there's no way to choose

##### **Geohot** [[00:42:39](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2559)]
i don't know yeah

##### **Geohot** [[00:42:52](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2572)]
Anything else?

##### **Qazalin** [[00:42:54](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2574)]
No.

##### **Geohot** [[00:42:57](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2577)]
I think Mellanox kind of works. I need to clean up this. Yeah, okay, sounds good. Next is this and SQTT stuff. This is the exec-to-dispatch linker here, and also the CLI access. What's the exec-to-dispatch linker?

##### **Qazalin** [[00:43:30](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2610)]
Uh, the line in the web viz that connects the execs to dispatch.

##### **Geohot** [[00:43:37](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2617)]
Oh, the lines. Yeah, the lines are very cool. Let me switch to `VIZ=2`. Why was RDNA4 crashing, and are you confident that stuff's fixed?

##### **Qazalin** [[00:43:52](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2632)]
Uh, I fixed it, by the marker, yeah.

##### **Geohot** [[00:43:55](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2635)]
Uh, but are you confident that stuff's fixed? I'm pretty confident there's not more issues like that.

##### **Geohot** [[00:44:03](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2643)]
You said that the instr number is telling you the number of cycles it takes.

##### **Qazalin** [[00:44:14](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2654)]
Oh yes, I think they put it in the enum.

##### **Geohot** [[00:44:20](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2660)]
Well, that's so interesting because when I was looking at those things for RDNA3, I was super confused and I almost felt like there was a bug because the loads and the stores were like slightly overlapped. Like the loads were like 0, 1, 2, 3, 4, and then the stores were like 4, 3, 4, 5, 6, 7. And I was like, why does a load and a store have the same number? This doesn't make any sense. But if it's the number of cycles, that's amazing. Actually it's only on RDNA4? I'm pretty sure it's on RDNA3 too.

##### **Qazalin** [[00:45:04](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2704)]
Uh yeah, they call it some different things. Maybe they just updated RDNA4, but...

##### **Geohot** [[00:45:10](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2710)]
Uh yeah, I mean it just feels like, here, I'll paste something. Here's like a viz wave pointing to VMEM, and it looks like those things are actually two cycles.

##### **Geohot** [[00:45:28](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2728)]
And VMEM, those VMEM ops are two cycles.

##### **Geohot** [[00:45:33](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2733)]
That would be my guess right now. I wonder what the instruction type is, if the type tells you it's two cycles.

##### **Geohot** [[00:45:47](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2747)]
But yeah, I would have Claude

##### **Geohot** [[00:45:54](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2754)]
try using the SQTT thing to get a fast, like, a fast WMMA GEMM, and we should make sure the tooling is good enough that LLMs can

##### **Geohot** [[00:46:11](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2771)]
just do that with the tool.

##### **Geohot** [[00:46:16](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2776)]
I don't think we should be thinking about how fast our GEMMs are. I think we should think about how fast of a GEMM we can get in an hour with Claude. Basically, I'll make like an auto-research repo

##### **Geohot** [[00:46:30](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2790)]
that uses tinygrad, and then yeah, we'll give it a time and a FLOP target and see how far it gets.

##### **Geohot** [[00:46:41](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2801)]
Also, you want to move that tool from `extra` into main tinygrad?

##### **Qazalin** [[00:46:49](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2809)]
Uh yeah, sure. I mean, I want to polish it. It's only two days old.

##### **Geohot** [[00:46:56](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2816)]
All right. Keep it where it is till you feel it's good.

##### **Qazalin** [[00:46:58](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2818)]
Yeah, I'm considering... I have the PR and I made this. I like this for humans. I'm considering removing `limit` and/or `offset`, and you were complaining about those APIs being...

##### **Geohot** [[00:47:14](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2834)]
Think about the API people really want. You want to pipe it.

##### **Geohot** [[00:47:22](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2842)]
Well, humans might pipe it to `more` or something, but LLMs aren't going to do that. And I'm not even sure humans really want to do that either.

##### **Geohot** [[00:47:37](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2857)]
So what would you want? Not sure.

##### **Qazalin** [[00:47:44](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2864)]
Okay

##### **Geohot** [[00:47:47](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2867)]
Yeah, maybe `limit` and `offset` are okay.

##### **Geohot** [[00:47:50](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2870)]
I mean, I would see how the LLMs use it, and I would play with it yourself and just find some happy compromise.

##### **Qazalin** [[00:47:56](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2876)]
Yeah

##### **Geohot** [[00:48:01](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2881)]
I like the arrow keys working. Oh, the arrow keys just integrated? The arrow keys existed like two

##### **Qazalin** [[00:48:09](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2889)]
Two weeks, yeah. Now the links are very nice. I want the web to lean into the visual cortex of the humans, and the LLMs can worry about the details.

##### **Geohot** [[00:48:25](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2905)]
Yeah, I mean, looking at this visually is so good. I wish the LLMs were better at that. How's SQTT on CDNA? Is it still unusable?

##### **Qazalin** [[00:48:38](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2918)]
Oh, for CDNA I merged the emulator.

##### **Geohot** [[00:48:41](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2921)]
The emulator?

##### **Qazalin** [[00:48:43](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2923)]
The emulator runs the assembly. Yeah, cool.

##### **Geohot** [[00:48:46](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2926)]
How about SQTT for CDNA?

##### **Qazalin** [[00:48:50](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2930)]
No SQTT work. That was new.

##### **Geohot** [[00:48:54](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2934)]
Yeah, like I don't know why it's

##### **Geohot** [[00:48:57](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2937)]
The traces look broken There's something we're missing

##### **Qazalin** [[00:49:02](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2942)]
Yeah, I don't know. I'm just saying this is exactly how it works.

##### **Geohot** [[00:49:08](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2948)]
It's just a different architecture We're not used to Who says this is how it works? It just looks wrong to me

##### **Geohot** [[00:49:24](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2964)]
Like what I see is like one trace with one wave Like it may only be one wave But there's definitely more information in there About like the different subunits and stuff like that And how they're being used

##### **Geohot** [[00:49:43](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2983)]
Oh, also for the viz CLI tool, are the kernel execs still called devices? I should probably call them something generic.

##### **Qazalin** [[00:49:57](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=2997)]
Yeah, they're called devices

##### **Geohot** [[00:50:00](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3000)]
Yeah I don't know They're definitely Definitely not devices

##### **Qazalin** [[00:50:05](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3005)]
They're not devices, yes

##### **Geohot** [[00:50:07](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3007)]
But they use the same idea Once again Anything else? No, I can't

##### **Qazalin** [[00:50:27](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3027)]
Great

##### **Chenyu** [[00:50:31](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3031)]
Do we have any karma complaints? Have they upgraded to the latest and greatest tinygrad?

##### **Chrism** [[00:50:38](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3038)]
I think they have not Something that's slow I don't know Arman said he's going to take a look at this And try and give me something more reproducible Because he was like, oh, this thing is slow And then he's like, he ran it himself And said that it wasn't slow I don't know So I just want to try and be on him a little bit more To give me something that I can actually work with To figure out what exactly is blocking them But it's some automated step in our CI That says this thing is slow And then I don't know exactly I tried to look into it a little bit And it seemed kind of complicated And I was like, okay, like, you know It would be a lot easier if they said, okay Like, here's the thing that's slow Here's the issue

##### **Geohot** [[00:51:24](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3084)]
So I'm going to try and get that from them And sort this out

##### **Qazalin** [[00:51:33](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3093)]
Okay

##### **Geohot** [[00:51:35](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3095)]
I think we'll Fatou, you want to say something about your training? Not a whole lot

##### **Flata** [[00:51:47](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3107)]
Just got the training loop going on I got the first step But I think I used Cloud And just some optimizations I think I used some batch optimization For the part of Cloud And just some parameters Because there was a lot So I'm still cleaning it up And looking to see if I can put up a PR for it

##### **Geohot** [[00:52:10](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3130)]
So this is training stable diffusion Or flux Yes, or flux, yeah Does it have attention? It does You want flash attention? How slow is the check? Sure

##### **Flata** [[00:52:28](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3148)]
I haven't measured it yet But it's still pretty slow Probably like over a minute, I think Probably even more

##### **Geohot** [[00:52:36](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3156)]
Over a minute And then how many steps do you have to do?

##### **Flata** [[00:52:41](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3161)]
I think until it converges There's a metric there So you kind of have to stop Like at a certain amount of steps And then you can evaluate from there And you have to kind of keep going

##### **Geohot** [[00:52:51](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3171)]
But I mean more for like For the other ones What have you seen?

##### **Geohot** [[00:53:01](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3181)]
Like the compared to the other How long did those ones take?

##### **Geohot** [[00:53:05](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3185)]
How many steps?

##### **Flata** [[00:53:06](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3186)]
Oh, the other reference ones I have to take a look again What NVIDIA I think NVIDIA has one for sure On that But they had like bigger clusters

##### **Geohot** [[00:53:17](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3197)]
Yeah, just like Yeah, figure out the number of steps Figure out what steps we need to get a reasonable time And then do you actually want to try to submit for this?

##### **Qazalin** [[00:53:29](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3209)]
Yeah Yeah

##### **Geohot** [[00:53:30](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3210)]
This round

##### **Flata** [[00:53:34](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3214)]
Probably not this round I feel like it's too close I think the next round I think it's probably around October, November I think that one is probably more suitable

##### **Chenyu** [[00:53:48](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3228)]
This round is May 11th Next is probably October, mid-October They have a date I'll find it and post it later

##### **Geohot** [[00:54:00](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3240)]
I need to pray they don't remove 4.05 I doubt they would But I don't know And what else? I think bounty

##### **Chenyu** [[00:54:14](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3254)]
The Qwen one looks good, but it's just going to be upstream, finally.

##### **Geohot** [[00:54:22](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3262)]
Yeah, I mean, what are the other tools? Like, what if I just Google right now, like, `Qwen 3.5 35B Strix Halo`

##### **Geohot** [[00:54:31](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3271)]
tokens per sec, what do I get?

##### **Chenyu** [[00:54:36](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3276)]
I imagine you will see a very similar thing on the `SGLang` and `vLLM` side. They either just don't work or they didn't optimize for it. They're getting 20.

##### **Geohot** [[00:54:50](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3290)]
Oh no, that's not with 4 Oh Yeah, they're faster with Q6

##### **Geohot** [[00:54:58](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3298)]
Than they are with Q4 I think we're using Q4 It looks like their fastest one Is 43 tokens per second So if we're getting 48, that's great Great

##### **Chenyu** [[00:55:29](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3329)]
So can we go through the old PRs And people close some of the old stuff We have a lot of PRs now

##### **Geohot** [[00:55:40](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3340)]
Sounds good Okay Go to VR That's awesome That's from 14 days ago Wait, we're actually going to win We got something I believe We get a gold

##### **Chenyu** [[00:56:02](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3362)]
I think that's lottery It's

##### **Geohot** [[00:56:10](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3370)]
So Oh It's Get Monthly It's Pretty Plenty

##### **Qazalin** [[00:56:25](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3385)]
Of

##### **Geohot** [[00:56:28](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3388)]
OK, sounds good.

##### **Chenyu** [[00:56:31](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3391)]
I imagine B1TG would listen to this recording. So just put whatever update or questions you have in terms of high-level design, if you have any in the corresponding channels, and we will resolve it there.

##### **Geohot** [[00:56:50](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3410)]
Let me look at that one. That's amazing. People might actually use this. Great, sounds good. Open issue.

##### **Geohot** [[00:57:07](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3427)]
Also, Qwen 27B, it's going to be slow, but it's not a mixture of experts. But apparently that one does really well on ClawBench.

##### **Geohot** [[00:57:21](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3441)]
Oh, yeah, 27 performs much better than 35,

##### **Flata** [[00:57:24](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3444)]
because 35 just has too little active RAM. Yeah.

##### **Geohot** [[00:57:30](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3450)]
Oh, it was number one. Oh, GPT just overtook it. But the number two model on PinchBench after GPT-5.4 is Qwen 27B.

##### **Geohot** [[00:57:51](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3471)]
So we should make sure we got that one working too. That one also might be a really good one to run on, I think, for any Radeon. Interesting. OK, great. Sounds good.

##### **Chenyu** [[00:58:06](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3486)]
I think that's it for this meeting. Thank you, everyone. See you next week, same time. Bye-bye.

##### **Geohot** [[00:58:12](https://www.youtube.com/watch?v=7rTl4VVHDdI&t=3492)]
Bye.
