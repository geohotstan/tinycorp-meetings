# 2026-01-19 Meeting

### Meeting Agenda

**Time:** 9am Monday San Diego time (random order)
- company update
- drivers
- image dtype
- assembly
- jit asserts, assign, MyPy
- LLaMA training
- viz / fast gemm
- other bounties

### Audio

[Youtube Link](https://www.youtube.com/watch?v=vQY3NbmWoJw)

### Highlights

- **[Company Update: focus on AMD + comma users](#geohot-000016)**: Emphasizes the AMD contract as mission-critical; asks everyone to focus work on either the AMD contract or improving comma workflows (the two paying users).
- **[Local models outlook](#geohot-000323)**: Predicts running models locally will matter more as cloud subsidies/controls tighten; argues the “box” is compelling, but software must catch up.
- **[AMD contract → future hardware leverage](#geohot-000455)**: Notes doing well could unlock better AMD hardware deals; expects chip tapeout is years away, so near-term strategy is buying GPUs smartly (e.g., MI350X / RDNA5) via the relationship.
- **[Drivers: Mac USB eGPU status](#nimlgen-000558)**: Reports Mac USB GPU driver is written and install UX is improved; Apple notarization (especially Dext) is the long pole, but should be faster once stable.
- **[Driver install UX: auto-detect + auto-install](#geohot-000935)**: Wants `pip install tinygrad` to detect an eGPU quickly, install/update drivers automatically, and avoid impacting users without eGPUs (important for selling eGPU boxes).
- **[Distribute binaries to avoid Xcode requirement](#nimlgen-001056)**: Suggests distributing prebuilt/unsigned binaries so users don’t need Xcode/build-from-source, even if SIP-related constraints exist.
- **[Beam stability: reduce HCQ timeout](#geohot-001310)**: Proposes lowering HCQ timeout from 30s (maybe to ~5s first), balancing crash detection vs legitimately long kernels; agrees to investigate.
- **[Beam timing accuracy issues](#geohot-001434)**: Observes Beam timing can differ significantly from final timings (up to ~3x) and wants to understand why (scheduling/global effects) to improve correctness.
- **[Image dtype & C types direction](#chrism-001832)**: Chrism focuses on making `image=1` fast enough to remove the image dtype path; keeps recent C-types structure changes (and tests DSL usability) to avoid relying on “janky” ctypes behavior.
- **[Renderer/compiler cleanup + maintainability first](#geohot-002453)**: Agrees renderers shouldn’t depend on backend device details; reiterates priority is simple/maintainable/bug-free code over speed/features; calls compiler-pair refactor + `image=1` as sprint goals.
- **[Assembly: switch to AMD XML + typed operands](#geohot-002630)**: Moves from PDFs to AMD XML instruction specs to type-check operands/register classes; disassembler+round-trip works for CDNA/RDNA3/RDNA4; assembler path cut for now.
- **[Emulator as a kernel dev environment](#geohot-002630)**: Building an emulator that compiles instruction blocks into TinyGrad programs, aiming for a clean foundation for handwritten MLPerf kernels.
- **[JIT asserts: block data-dependent reads](#chenyu-002946)**: Chenyu adds/asserts against using `_buffers` via `tolist()`/`item()` in JIT (mask/data-dependent patterns); finds/fixes an Onyx gather “const” fastpath that caused underlying-buffer issues.
- **[Assign correctness overhaul](#chenyu-002946)**: Builds a large test suite and fixes read-after-write/write-after-read hazards; goal is removing TODOs like “add realize/contiguous here” and cleaning up disk tensor lazy hacks by fixing root scheduling/assign behavior.
- **[Remove disk tensor workarounds](#geohot-003357)**: Calls out disk tensor conditionals/hacks as especially desirable to delete once core correctness is fixed.
- **[Setitem no longer forces realize](#chenyu-003453)**: With the new fixes, `setitem` doesn’t realize, which Geohot calls a big win for practical workflows.
- **[Typed/MyPy regression: `invalid` in mixins](#geohot-003824)**: Diagnoses MyPy/type issues around `invalid` mixing tensor/UOP/const usage; wants `typed=1` to fully pass (and eventually be in CI).
- **[LLaMA training: flash-attn progress](#wozeparrot-004018)**: Reports BERT training works with flash attention (though performance comparisons aren’t apples-to-apples yet); sprint goal is LLaMA 8B training.
- **[Urgency: MLPerf-qualifying LLaMA 8B ASAP](#geohot-004112)**: Geohot is concerned LLaMA 8B qualifying training didn’t land last sprint; stresses performance is secondary to correctness/qualification, and wants it “as soon as possible.”
- **[Daily iteration plan on LLaMA 8B](#geohot-004358)**: Expects ~2-hour runs, enabling a full training run every day; plan is to qualify first, then add tricks (grad accumulation, model splitting, checkpointing) on 8B before scaling up.
- **[SQTT viz: CDNA support + tie packets to PC](#geohot-004613)**: Asks for CDNA support in the unpacker but limits effort to ~1 day; prioritizes visualization work: map packets back to instructions/PC reliably, fix barrier extents, and handle “wave ready” packets.
- **[Fast GEMM: support rectangular matrices](#geohot-005341)**: Pushes for GEMM that handles non-square shapes (M/N/K), viewing it as “free speedup” for training; suggests using Torch behavior/dumps as reference.
- **[MLPerf: generate ELF directly](#qazalin-005440)**: Qazalin says the “ELF directly generated” work is done (had a master-merge break, then fixed); Geohot asks for cleanup/review quality before merging.
- **[Bounties + AI code quality concerns](#geohot-005838)**: Frustration with bounty submissions that look copy-pasted from AI; notes the hard part is validating correctness, and warns AI can drive unproductive rabbit holes.
- **[Wrap-up](#chenyu-010014)**: Meeting ends; Chenyu thanks everyone and closes.


### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=0)]
First, welcome everyone to our third meeting, our third new meeting.

##### **Geohot** [[00:00:05](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=5)]
I did render an order for the middle store, but let's still start with company update.

##### **Geohot** [[00:00:15](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=15)]
Thanks.

##### **Geohot** [[00:00:16](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=16)]
One, I want to emphasize how important it is, AMD contract. I think that the ideal contract is the dream thing to work on training LLaMA four or five V on ML turf. Not really. But two things about that is that is what everybody kind of wants. One thing that everybody wants is to be able to train large transformers. This is what Kama wants. This is what anybody who wants. This is what anybody who's trying to clone Claude code wants. So it is very useful. And then the other thing is I think that this contract is really important. Like these things are really hard to get. It's not easy to get a contract with a large company to basically do work for them on something like this. Right. And you can say that, oh, it's, you know, I bullied them on Twitter or whatever, but I think it's. It's more than that. Right. I think that we have a contract and we should really put forward everything to get it done. So really everything should be focused on either that on our other customer comma and improving their workflows because we have we have two actual. Going to pay money to use tiny grad, but one is AMD and one is comma. So everything should be focused on one of those two things. Right. So. I think that's the most important thing. And I think it's also important to think about, you know, in the context of open code being banned from Claude code. I wonder how long it is. Land traffic actually just started doing account bans. And then I'm like, OK, so if you have to run local models, what do you have to run? And then you realize that what you probably want to buy is a TinyBox screen Blackwell and you want to run you want if you with six of those, you could maybe barely run the ZI model. Yeah. I think these things are going to become more and more important. I think more and more people are going to start to want to actually run models locally. They're not making money on it. So, yeah, I wonder what the real cost of that is. The real cost of that is two thousand dollars. Suddenly buying that TinyBox. So it's seemed like a really good deal. So I want everything focused on either the AMD contract or the. Comma. Use cases because these are actual users.

##### **Geohot** [[00:02:59](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=179)]
And yeah.

##### **Geohot** [[00:03:06](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=186)]
The two in the morning. Yeah. So if this is if this is my life now, I wake up in the middle of the night. You get me.

##### **Chenyu** [[00:03:15](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=195)]
You were caught up a little bit, at least for me, specifically for running local models.

##### **Geohot** [[00:03:23](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=203)]
I think. I think that Anthropic is subsidizing the cloud plan that everybody's using now. I mean, they have to be because otherwise, why would they care so much if you're using open code? So I think that. Yeah, I think that in the next year, I think it's going to start to become really, really important. Like, I think people are really going to want to run open models as the clouds and shit apply. So, you know, we have the box to do it. We just need to have the software to do it. Okay. That's good. Yeah. The AMD contract is super, super important. The contract also potentially gives us the ability to, like, work with AMD to buy.

##### **Geohot** [[00:04:15](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=255)]
I cannot hear you after to buy if you are saying something.

##### **Chrism** [[00:04:19](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=259)]
Oh, yeah. Yeah.

##### **Geohot** [[00:04:20](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=260)]
Let me see what's going on on.

##### **Geohot** [[00:04:26](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=266)]
Also not clear if it's me or it's you.

##### **Geohot** [[00:04:30](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=270)]
Is that better?

##### **Geohot** [[00:04:33](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=273)]
I don't know.

##### **Geohot** [[00:04:34](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=274)]
Continue talking more input sensitivity here to two microphones, so I can try the built in mic to my I can try the AirPods. That's from the AirPods. Is that better?

##### **Chrism** [[00:04:47](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=287)]
Yeah.

##### **Geohot** [[00:04:50](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=290)]
I think so. Maybe continue talking. Is this one good?

##### **Geohot** [[00:04:53](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=293)]
Okay.

##### **Geohot** [[00:04:55](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=295)]
Yeah, I don't know what's going on. But yeah, the AMD contract is super important because doing well in the AMD contract gives us the ability to work with AMD to get good deals on hardware. Realistically, it's going to be a long, long time, at least three years before we can tape out a chip. And in those three years, what do we want to buy? Do we want to buy MI350X chips? Do we want to buy RDNA5 chips? Let's do well in the AMD contract.

##### **Geohot** [[00:05:38](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=338)]
Okay. I feel you're still cut off.

##### **Chenyu** [[00:05:45](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=345)]
But it's taken. We can move on. I have a random order. I have a random order this week.

##### **Geohot** [[00:05:50](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=350)]
So let's start with drivers.

##### **Nimlgen** [[00:05:58](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=358)]
Yeah, so I've been focusing on Mac USB GPU.

##### **Nimlgen** [[00:06:06](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=366)]
So yeah, it's completely written. It should be a lot better user experience to install it. So it's also.. I know you checked this site, but this time it was at a cost of $80000 thousand. More cettez is good for Mac USB, but just don't start using Mac USB. And for a Plus Plus support, you can check Ulna on the other side of Apple. And the Vsta has released a lot of plugins for Johnny Carr for Vsta sta, the need for cPi voltar or a lot of cybersecurity problems, all of this stuff. Now to Vsta. So, you know, we're still waiting for an authorization.

##### **Geohot** [[00:06:58](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=418)]
Yeah. So, we have to do the notarization every time?

##### **Geohot** [[00:07:06](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=426)]
Yeah. Yeah. I don't know.

##### **Nimlgen** [[00:07:13](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=433)]
No, I mean, like, for, as far as I understand, like, their documentation, we have to do authorization. Like, we will get two different authorizations for the application and for the Dext. And I think Dext is what takes a lot of time. And if we keep it unchanged, so it will be faster next times.

##### **Geohot** [[00:07:41](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=461)]
Yeah. I mean, even if we're still disabled. Yeah. Improving the install process is definitely worth it. It was super annoying to install the old one. Like, that app to install it was, like, buggy. So, is it now, like, does it launch it from TinyGrad?

##### **Nimlgen** [[00:08:00](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=480)]
Yeah. I mean, what exactly?

##### **Geohot** [[00:08:04](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=484)]
Like, the install? Yeah. Installation?

##### **Nimlgen** [[00:08:09](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=489)]
No.

##### **Chrism** [[00:08:11](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=491)]
No.

##### **Nimlgen** [[00:08:13](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=493)]
No. There is separate script, which you just run the script and install the application. How do I know? It actually builds the application.

##### **Geohot** [[00:08:22](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=502)]
How do I know to install that script?

##### **Geohot** [[00:08:26](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=506)]
I mean, yeah. I mean.

##### **Chrism** [[00:08:31](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=511)]
I mean.

##### **Geohot** [[00:08:34](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=514)]
No, I probably can.

##### **Chrism** [[00:08:40](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=520)]
Yeah.

##### **Geohot** [[00:08:44](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=524)]
Yeah. Yeah.

##### **Nimlgen** [[00:08:45](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=525)]
I mean, I can race and, like, publish some instruction to do that. I think also I can install this in TinyGrad. But I don't know. That will be annoying, like, if you don't want to install this. But like the AMD is the top priority. I mean, like the backend is top priority. It will just try to go and just try to install and all these things. And only after that, it will detect that there is no GPU.

##### **Geohot** [[00:09:13](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=553)]
We can't detect if there's a GPU plugged in without having it installed?

##### **Nimlgen** [[00:09:23](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=563)]
Probably we can.

##### **Nimlgen** [[00:09:26](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=566)]
Like, I have this functionality in the app to detect if we have the GPU in all PCI devices.

##### **Geohot** [[00:09:35](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=575)]
I mean, the workflow that would be really good is if TinyGrad just detects quickly that, there is an eGPU plugged in. And then it sees if the thing is installed or it needs to be updated. And then it does that. And then.

##### **Geohot** [[00:09:55](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=595)]
Yeah. But actually, the problem is that. And I think, I think it's good. Yeah. Yeah. Yeah.

##### **Nimlgen** [[00:10:06](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=606)]
I can do that.

##### **Chrism** [[00:10:09](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=609)]
Cool.

##### **Geohot** [[00:10:11](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=611)]
Just want, like, a little bit of a. Because we're going to start selling these eGPU boxes. Just be pip install TinyGrad on something. And it's like, oh, I've detected you have an eGPU. Okay. Let me install the driver. But then not interfere with people's workflow who don't have an eGPU.

##### **Geohot** [[00:10:33](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=633)]
Yeah. Yeah. This should work.

##### **Nimlgen** [[00:10:38](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=638)]
Yeah.

##### **Geohot** [[00:10:40](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=640)]
Yeah. Because, like, having to know to do the extra thing. And then even if people disable SIP, do they have to have Xcode installed?

##### **Geohot** [[00:10:54](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=654)]
No, I think. No.

##### **Nimlgen** [[00:10:56](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=656)]
No. I mean, currently, yeah. Because currently, like, for, like, the script just builds from the sources if you have no SIP. But I think, yeah, I can just distribute completely unsigned data. And then binarying it will be fine.

##### **Geohot** [[00:11:31](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=691)]
Did you look into the Beam issues on BERT?

##### **Chrism** [[00:11:38](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=698)]
Yeah.

##### **Geohot** [[00:11:40](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=700)]
Yeah. No.

##### **Nimlgen** [[00:11:44](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=704)]
I think Prosperity you can share, like, branch and maybe comment with me. And I'll take a look into this if you have no time. Yes.

##### **Wozeparrot** [[00:11:53](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=713)]
We will. I'll look into it a little bit. And then I'll also send you a reproduction branch. Yeah.

##### **Geohot** [[00:12:03](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=723)]
So I think in general, we want to lower that HCQ timeout there.

##### **Chrism** [[00:12:10](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=730)]
Yeah. Cool.

##### **Geohot** [[00:12:15](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=735)]
Do we ever have a kernel that takes more than a second? You said we want to lower it. Yeah, wait, let me switch to my phone if something's not working right.

##### **Chrism** [[00:13:00](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=780)]
We'll wait for what happens.

##### **Geohot** [[00:13:03](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=783)]
Yeah. All right. Jay, do you want to start?

##### **Chrism** [[00:13:09](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=789)]
Yeah.

##### **Geohot** [[00:13:10](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=790)]
Oh, okay. So if we could lower the HTQ timeout from 30 seconds to like one second or something.

##### **Geohot** [[00:13:21](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=801)]
I mean, yeah, the problem is that we can have kernels which take longer.

##### **Nimlgen** [[00:13:30](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=810)]
And actually for our drivers, we can detect that state faster than 30 seconds, like if we have

##### **Geohot** [[00:13:37](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=817)]
page files. Should any kernels take longer than a second? Of course, there are tons of kernels

##### **Chenyu** [[00:13:46](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=826)]
that can take more than a second. Really? Like what? Like a really badly written get item kernel

##### **Geohot** [[00:13:56](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=836)]
that has a very big reduce. It's forever. What's the longest kernel we've ever seen?

##### **Nimlgen** [[00:14:15](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=855)]
I think one time we even increased these 30 seconds for some beaming. I don't remember

##### **Geohot** [[00:14:21](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=861)]
what exactly. So now if things crash, we're detecting it faster, right?

##### **Geohot** [[00:14:28](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=868)]
Yeah.

##### **Geohot** [[00:14:34](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=874)]
The other thing that I'm interested in looking into is the kernel that we're using. I think it's called the kernel kernel. And it's like, so a lot of times on my computer, I'll do beam. And the timings for beam will be pretty different from the final timings. And I'm not sure why this is like off by like three x.

##### **Geohot** [[00:14:59](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=899)]
Yeah, I see. Yeah, I wonder if this is because of like the global thing.

##### **Chenyu** [[00:15:09](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=909)]
Yeah. I remember before even if I disabled the test size and try with the fresh thing increase the count from your sampling, there still can be off. But it's not clear if it is because it's running sequentially with other kernels. So it's scheduled differently on the hardware or something like

##### **Geohot** [[00:15:32](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=932)]
that. Yeah, I mean, I'm curious to understand this and just

##### **Geohot** [[00:15:37](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=937)]
just like improve beam on AMD in general. I think it's also not just on AMD. I think at least for metal.

##### **Geohot** [[00:15:55](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=955)]
Is it possible to set the HCQ timeout dynamically? Because really you want to stop it anyway when you hit the upper bound of the longest kernel in the pass-through.

##### **Chenyu** [[00:16:10](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=970)]
Because setting a threshold dynamically is always like janky and hard to maintain. Maybe like a realistic start is to have a proxy less static and know if this kernel should be run long or short. Something similar to the UOP limit. If it has like tons of UOP, then it's likely to take longer. Something like that. So it's not like we don't want to change the threshold dynamically, but we want to make sure that it's not like we don't want to change the threshold dynamically, but we want to make sure that it's not like we don't want to change the threshold dynamically, but we want to understand the underlying workload better.

##### **Geohot** [[00:16:44](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=1004)]
If something needs to take long, then so be it. Which one would you just. Maybe less dynamic. Can we lower it to five seconds? Can we start with five seconds? Yeah, we can try. I think yeah.

##### **Nimlgen** [[00:17:06](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=1026)]
Yeah. Yeah, I'll take a look into the timings during Beam. Cool.

##### **Geohot** [[00:17:14](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=1034)]
And then as kind of a stretch goal for the sprint,

##### **Geohot** [[00:17:18](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=1038)]
what does AMD have like SQTT? Sorry? You mean Nvidia like SQTT? Sorry, Nvidia, yeah. Yeah.

##### **Nimlgen** [[00:17:36](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=1056)]
Actually, no idea. I can look into that.

##### **Chrism** [[00:17:42](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=1062)]
Cool.

##### **Geohot** [[00:17:43](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=1063)]
Yeah, just that we're doing the visualizer and thinking about it.

##### **Geohot** [[00:17:46](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=1066)]
I always like to have both. Yeah, the main thing is stability of the driver. And correctness of Beam timings. OK. OK. Next for image D type and C type. Yeah. Sorry.

##### **Chrism** [[00:18:32](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=1112)]
OK. OK. Yeah. I mean, so the thing that I worked on last week was mostly this C type's structure removal. I think maybe the test for this is whether or not the AMD DSL can use it. And if it's not usable, then I guess, I don't know. I mean, I think it's still worthwhile. I mean, we discussed this a little bit. I think it's still worthwhile to keep it around because of not relying on this sort of. Yeah. I think it's still worthwhile to keep it around because of not relying on this sort of janky C type's implementation. But yeah. And then this week I'm going to focus on getting image equals 1 to be fast. And if that works out, then image D type can go. But obviously it can't go until image equals 1 is faster

##### **Geohot** [[00:19:21](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=1161)]
than image equals 2. Yeah.

##### **Geohot** [[00:19:28](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=1168)]
I think we should leave the new C type structure for now. I did things a bit differently in the DSL. So the way that I saw you did C type structure was that the actual types that are in the Python object are ints and that they're packed on store. Yeah. So I did it a bit different. I don't know. I'll look into this. I'll look into seeing if I could unify them. I did it basically the types on the things that are in the Python object are the packed types. It creates a class for each thing, which might actually be slower. So I'll look at reusing the root from C type structure. But I don't think we'll be able to.

##### **Chrism** [[00:20:18](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=1218)]
Yeah. Go ahead. Oh, the reason I did it like that was just because when you access a field on a structure, you get an int back or you get a bytes object back or a float back. Yeah. Or whatever. So I just wanted the MyPy stuff to be accurate.

##### **Geohot** [[00:20:36](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=1236)]
Yeah. No, when you access a field on the DSL stuff, you'll get a special vgpr type back. I see.

##### **Chrism** [[00:20:47](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=1247)]
Yeah, we could have the fields of the structures give back the C types object. The problem with this is then you have to put dot value literally everywhere. So that's kind of annoying.

##### **Geohot** [[00:20:57](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=1257)]
Yeah, I think it might actually just be a different use case. But either way. I think the C type structure changes in. I'm happy with it. Let's not mess with it anymore. Yeah, I agree. Yeah. Image equals one and then anything to support the main goal of the company, which is training the AMD.

##### **Chrism** [[00:21:23](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=1283)]
Yeah, yeah, yeah, yeah, for sure. I mean, so I think the focus is image equals one for this week. The other thing that we talked about, I think, is that we're going to be doing a lot of work on this. And then I think the last thing that we talked about previously, which probably shouldn't be a focus, but I mentioned it, is the compiler pair removal. I don't know. This is obviously much less important.

##### **Geohot** [[00:21:46](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=1306)]
No, I mean, I think the compiler pair removal is pretty important. You said you wanted to remove the device from the renderer?

##### **Chrism** [[00:21:53](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=1313)]
Yeah. So I mean, I don't know. This is maybe. Maybe I just have an innate bias against this sort of object rendering. This is the most sophisticated programming style of API. So maybe this is just, I don't know. Like maybe I'm totally off base here. But it seems very awkward to me that we have like hip renderer and AMD hip renderer and AMD hip CC renderer. And then similarly we'd have like NVCC renderer and then CUDA NVCC renderer and then CUDA NVRTC renderer and whatever. Like this seems, I mean, I guess it's fine, but it seems a little bit messy considering they all basically do the same thing. And the only thing you're parameterizing over is what compiler you're using. But then it's kind of like, okay, well, if your renderer accepts a compiler argument, then how is this fundamentally different than compiler pair?

##### **Geohot** [[00:22:42](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=1362)]
Because it's one object and it's pre-created somewhere else, right? So yeah, the problem with compiler pair is mostly, I just don't like the way that it's like structured.

##### **Chrism** [[00:22:59](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=1379)]
Hmm.

##### **Geohot** [[00:23:00](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=1380)]
I think that there's no distinction between rendering and compilation. So yeah, I mean, I don't think that there's anything wrong with having lots of those objects. That seems totally fine to me. Like you have an object. Yeah. Like the point of that object, the point of, of, of, of AMD hip CC compiler is to, to do a workflow that transforms UOPs into bytecode. Yeah. Yeah. Right. Right. And you're going to fundamentally need some object to capture that workflow.

##### **Chrism** [[00:23:32](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=1412)]
Hmm.

##### **Geohot** [[00:23:34](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=1414)]
Right now, what were you imagining? It'd be, it's something that's more like compositional.

##### **Chrism** [[00:23:39](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=1419)]
Yeah. I mean, I guess basically like the thing is like, uh, like there's no difference between the CUDA NVRTC renderer in this case and the NVRTC renderer, or sorry, the NVRTC renderer, because they're like, they're both doing the exact same operation. Uh, actually in this case, no. One of them is emitting PK. Yeah. And the other one is emitting PTX. But, but, uh, in general, like you could have, there's examples of this where they're, they're doing the exact same operation, but the only thing different is the renderer dot device.

##### **Geohot** [[00:24:06](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=1446)]
Well, that's okay. So that's a different issue. That's a different issue. And if you can fix that, I think that's a good idea. Right. But what you should think of as the renderer, the renderer is just a transformation from UOPs to, uh, binary. Yeah. Yeah. No, that makes sense. Yeah. Yeah. For every type of transformation. If you're doing one with, uh, hip CC, uh, binary, uh, binary, uh, binary, uh, binary, uh, binary, you know, hip and then calling hip CC, hip, and then you're using co-manager, right, those should be separate render objects.

##### **Chrism** [[00:24:37](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=1477)]
Yeah. Yeah. No, that, that, that makes sense to me. Um, yeah, the, the, the, the best example for why this was like a sort of not, maybe not great is, is, is where you're, you're like the only thing different is the device and the actual renderer is just doing the exact same operation.

##### **Geohot** [[00:24:53](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=1493)]
Yeah. If you could refactor to remove that, that would be great. Like, yeah, I agree. that the CUDA, whether it's being run by the CUDA backend or the NV backend, the renderer should have no knowledge of that. Yeah. Okay. Cool. I think that actually is pretty important. I think that paying off.. Okay, so in general, coming back to the stuff about why we never do fast paths, the most important thing that we do with this company is that we keep the tiny grad code simple and maintainable and bug-free. Speed doesn't matter. Features don't matter. Nothing else.. All of speed, features, complexity, these things increase technical debt. And I think that in software in general, there is way, way, way too much technical debt. This doesn't exist in hardware. When someone's building a chair, they're not just going to import a 200-meg chair updater library and just be like, yeah, well, it's in there and it works. But yeah, so I think that things like the compiler-perry factor are quite important. And we should do that. I'm thinking about how to do.. Now that we have that.. Yeah, to get everything to work with the new program instruction. So then the lowering actually happens as a thing. Yeah, that makes sense. Image equals one in compiler-perry. Seem like good goals for the sprint.

##### **Chrism** [[00:26:19](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=1579)]
All right.

##### **Geohot** [[00:26:26](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=1586)]
Next is George, your assembly stuff.

##### **Geohot** [[00:26:30](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=1590)]
Yeah, so pretty good progress. You know, I should have started with the XML stuff and not the PDF stuff. The biggest thing that the XML has that the PDFs don't.. So AMD publishes these XML files that explain all the instructions. And the biggest thing the XML has is it explains the type of every operand. That turned out to be annoying. In everything. But I switched to the XML. So now everything is type-checked. So when you're doing a global load, the global load has to have the right number of registers for each argument. It has to be a VGPR if it's a VGPR, an SGPR if it's an SGPR. The offsets and stuff always were checked correctly. But yeah, now it checks the.. If it has to be a pair of registers, it's a pair of registers. Even though that's not actually encoded anywhere. It's not anywhere in the instruction type. Because the instruction just specifies the base register. And you have to just know that it's two. But I checked all that from the XML. So yeah, all that works. I cut the stuff that was doing the LLVM to our bytecode. So it can't function as an assembler. But all the disassembler stuff works. Disassembler and round trip work for CDNA, RDNA3, and VB4. And I'm going to do that. Quaslint, I saw you have that one MFMA instruction that doesn't work. We should fix that. If the hardware supports it, we should be able to express it. Yeah, and then what I've been working on for the last couple days is the emulator. I have an emulator now that compiles everything to actual TinyGrid programs. I think we can extend it to just do basic blocks. So we can just take a basic block of AMD instruction, and then we can just do basic blocks. As you can recognize, that's not happening here in the actual environment. and then do some clean-up mph as Körper mod imminent Airport MRI. But that's only the process. So I've got what's called behavior, not emulators, I've got the opposite, the supuesto cái equals the boundary logic. So I've hide them down one by one. I like that. Yeah. a nice development environment and a foundation that we can start to build on as we hand write the kernels for the ml perf contract. Yeah, so I think it is going to take the rest of the sprint also to make the code really clean. You know, a lot of it is written with Claude, but I'm aggressively going through it line by line. I think the code quality by the time this gets merged into TinyGradMaster will be on par with everything else that's in there.

##### **Geohot** [[00:29:28](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=1768)]
Well, I won't merge it if it's not. Sounds good. Next is my stuff.

##### **Chenyu** [[00:29:46](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=1786)]
So I mostly work on one is understand JIT issues. Which is a sign. I think two of the biggest things we know there are bugs or issues. So for JIT, it's mostly asserting the easy cases now. There is one that I'm working on. Basically, we want to assert when you s underscore buffers. Like if you call like to list or item and you use that in your answer function. So think about like mask field or anything that is data dependent. We want to assert that in JIT. So the check itself is easy, but then I run into another issue in Onyx that previously in Onyx as a hack or speed up for open pilot model. So I can see that it has a special path for gather. So if gathers input in indices is a const. It always assumes a const if it's small size. Then use the item basically from that to now treat it as a const and to special path. And that was causing issue because that obviously caused underlying buffer during JIT. So I fix that to be to detect from Onyx model. So first, at least make sure it only triggers when it's actually a const. Now I need to find a way to. I have list down in the Onyx cache stuff that's currently correct and pass the test, but I'm not too happy about that. So I want to also refactor that part. In Onyx, we do some special caching from the tensor to do like Python objects. And we want to make sure there is only one path for this. So. After that, I think JIT assert is in a pretty good places. I also went through all the open issues with JIT and try to either assert stuff or just fix it. The goal here is I hope once we understand the issue and have no like a known issue, then we can think about how do we want to refactor this, how to make it as simple as possible. Reuse. In the schedule cache and stuff like that. So that's JIT. Assign is more interesting because assign started with a lot of to do's in tiny grad examples, saying you must add a contiguous here or you must add a realize here. Otherwise it's wrong. Then turns out assign is just really broken and it doesn't handle many of the cases. So my current state is I wrote a very, big, I guess cloud wrote most of it. I just ask it to write a lot of cases for assign and how it was wrong previously. Now I have a giant PR that has 100 lines of. Handling the write after read and read after write and stuff like that to make sure it runs correctly. So my idea here is similar to JIT. Once I make sure all the cases I can think of. I can type. I can write a lot of cases. Then I would think about. The correct way to merge lists. Because some of this needs to be in the tensor level. Because the information you lose while you try to schedule it are very hard to recover while you try to lower it to schedule. But after this we can remove all the to do realize bug, to do contiguous bug. And another related thing is to make the disk tensor lazy bug. So I think that's a pretty nice place to be. So that's a sign.

##### **Geohot** [[00:33:57](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2037)]
It'd be great to remove those disk tensor hacks. Those like if disk tensor things.

##### **Chenyu** [[00:34:03](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2043)]
Yeah, the fundamental issue is. So I started this by working with cloud to fix that. Then you realize if you just fix it in the disk level, then it's tons of crap. And it's just because they're trying to work around the. The. The bugs in the assign and scheduler and render by around the area. Oh, I'm on this fighting to do and try to rule cause let's see the solution and realize it's another bug in another part. So I think that's pretty fundamental. So it's good to understand what's going on there.

##### **Geohot** [[00:34:42](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2082)]
When we do, do we have get item without realize? Does get item realize? No. How about setup? Set item.

##### **Chenyu** [[00:34:53](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2093)]
Set item with my fix? No.

##### **Geohot** [[00:34:58](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2098)]
Oh, that's great. Yeah. If you've said item doesn't realize now that's a big win.

##### **Chenyu** [[00:35:04](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2104)]
Yeah, you shouldn't realize or I guess the first thing cloud would do is find a place and add realize for you. But no, but the idea is how do you capture this dependency in? And now address action that you have but already mapped. ent. Yes. And I think 1 goes through the guy's browser and accept it often to the object asking. And here it is, so it's. It's actually compile grabbing time for the last few things as well. Because there are a lot of things that we might or may not want to do right. So you could just pick one directly from the API connection and maybe edit something, remove it or delete. Yeah. So we probably should do that by disrupting de utilities. Yeah.

##### **Geohot** [[00:35:49](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2149)]
Yeah, that seems right.

##### **Geohot** [[00:35:51](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2151)]
You look at the way that RL people use TinyGrad. They do tons of set item assigned stuff.

##### **Chenyu** [[00:35:59](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2159)]
Yeah, also I fixed another thing that issue. If you slice your window by a shift because there is a buffer reuse, then there is a bug. Something like that. So I think all these are pretty related, just some of the use case that we never fix. It's nice to fix those. One last thing I want to get fixed is, so I look into my PI, my PI reports, and two biggest issues that we have in precision, or I guess it's called any, like they simply cannot refer. One of it is the mixing. So you try to add return self to mixing. You got tons of errors. And a lot of lows, it's because of invalid. And this is slightly annoying because invalid is only a concept that should exist in uup. You should not use invalid in tensor on the ALUs. But the mixing currently support both.

##### **Geohot** [[00:37:09](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2229)]
Don't have a good solution there.

##### **Chenyu** [[00:37:13](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2233)]
Otherwise. You mean like? So if it not work, then you can't do anything. Now in invalid, sorry, now in mixing, those ALU function should return self type. Yeah, yeah.

##### **Geohot** [[00:37:25](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2245)]
They support tensor and uup. Yeah.

##### **Chenyu** [[00:37:29](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2249)]
But it also supports const type as like Python objects. Because you can do like, it applies ufix for you. So you should.

##### **Geohot** [[00:37:39](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2259)]
Oh, and you can put invalid in there, I see.

##### **Chenyu** [[00:37:42](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2262)]
Yeah. So the two practical solution is either, you know, you can do it. So adding invalid type to const is bad because tensor use that. And a lot of place that only accept Python use that. But if you don't except that, then if you try to run typed with a D equals to one and you'll complains about invalid and everywhere it doesn't accept invalid. Don't have a good solution though. But I will think about this more because I think this is like half of our MyPy, NOC, error, and also the main reason why type equals to 1 is wrong.

##### **Geohot** [[00:38:24](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2304)]
Yeah. I thought I fixed this. I thought that I have some stuff working with type equals 1. I have basic stuff working. Has that regressed?

##### **Chenyu** [[00:38:36](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2316)]
So I think previously, we only test the import statement is correct and not really anything.

##### **Geohot** [[00:38:45](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2325)]
I've run stuff with it. I've run test tiny with it.

##### **Chenyu** [[00:38:49](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2329)]
Well, then maybe it regressed with the new invalid. I don't know how recent this is. Oh, so I think it's maybe after we move more stuff to mixing that it regressed.

##### **Geohot** [[00:39:04](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2344)]
I see.

##### **Chenyu** [[00:39:06](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2346)]
Because previously, it's separate as two subset of functions, right? And it probably can infer that part of it except invalid, and the ones in tensor doesn't.

##### **Geohot** [[00:39:15](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2355)]
Yeah. Yeah, this must be some kind of regression, because this used to work. I see the invalid thing now. Yeah, yeah, yeah.

##### **Chenyu** [[00:39:27](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2367)]
Yeah, so working with Cloud, it seems to use any metadata type information it can use to try to guess what functions to use. So I think fixing this is useful in general. And also just makes you realize maybe there's some design errors, or something. Things like that.

##### **Geohot** [[00:39:46](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2386)]
No, I agree. I mean, that's why we have typed equals 1. It should eventually all pass with that. Yeah, I should put this in CI.

##### **Chenyu** [[00:39:57](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2397)]
We have the one import. And yes, once we fix this, I think wrong with test tiny, and if that pass, it seems pretty good.

##### **Geohot** [[00:40:11](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2411)]
Cool.

##### **Chrism** [[00:40:12](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2412)]
Yeah.

##### **Geohot** [[00:40:13](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2413)]
Next.

##### **Chenyu** [[00:40:16](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2416)]
So LLaMA training.

##### **Wozeparrot** [[00:40:18](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2418)]
So last week, we have a birch training with flash attention now. It's pretty good. It is slower than normal attention, but it's also not really comparable, because none of the two runs were beamed. We'll look into that. And then the goal of this sprint is mainly just to get LLaMA 8 training. And that should be fairly doable. And then I can start landing performance improvements. The backwards kernels are currently, there's three kernels, and it really should only be one kernel.

##### **Geohot** [[00:40:55](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2455)]
So yeah, I'm not worried about performance. I am worried that two people had on their sprint last week that we were going to have LLaMA 8b training, and we don't have LLaMA 8b training.

##### **Geohot** [[00:41:10](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2470)]
Yeah.

##### **Geohot** [[00:41:12](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2472)]
Yeah, so we need, regardless of performance, we need to get an MLPerf qualifying LLaMA 8b training as soon as possible.

##### **Wozeparrot** [[00:41:21](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2481)]
OK. I'll focus on that this week then.

##### **Geohot** [[00:41:25](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2485)]
Cool. Yeah. And then, so yeah, Burt works with flash attention. Did you run it with null and see how much RAM it uses?

##### **Wozeparrot** [[00:41:34](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2494)]
For LLaMA 8b?

##### **Geohot** [[00:41:36](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2496)]
Yeah, with the A192 context.

##### **Geohot** [[00:41:39](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2499)]
I haven't yet.

##### **Geohot** [[00:41:48](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2508)]
But yeah, no, this is, I mean, we have to get, if by the end of this sprint we don't have a LLaMA 8b qualifying training, I'm very worried.

##### **Geohot** [[00:42:04](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2524)]
Yeah. Yeah, is there anything that anyone can help with?

##### **Chenyu** [[00:42:14](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2534)]
I think we're good. I think the most important thing is making sure flash attention works and works correctly. Because one of the important things that we don't yet know is how many tricks we really need to, we still need to run for 5G. And we use Burt and we use 8b as a proxy to verify the flash attention works. But we all know that there might be, we need a lot more, like, 4 or 5b to work.

##### **Geohot** [[00:42:49](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2569)]
Why do you think? I think if we have 8b training, I think it's a pretty straightforward scale up, right? No.

##### **Geohot** [[00:42:56](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2576)]
Why? You need to split the model and you need to do gradient, gradient checkpointing. Oh, yeah, yeah, but that's not. And you might need float 8.

##### **Geohot** [[00:43:07](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2587)]
Well, if we need float 8, that's a bigger problem. But I'm not worried about splitting models

##### **Geohot** [[00:43:13](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2593)]
and gradient checkpointing. I'm definitely not worried about gradient checkpointing. I don't really understand splitting models.

##### **Chenyu** [[00:43:26](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2606)]
I think maybe just in general, it's just we don't quite yet understand the extra memories we need for computation now. So.

##### **Geohot** [[00:43:39](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2619)]
We can also start adding these tricks to LLaMA 8b. Like, we have to get a qualifying LLaMA 8b. Run as soon as possible. How long do we expect LLaMA 8b to take to train?

##### **Chenyu** [[00:43:52](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2632)]
They have two hours, right? Or a meg of that.

##### **Geohot** [[00:43:58](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2638)]
Yeah, so something we can comfortably iterate on and have a LLaMA 8b training every single day.

##### **Chenyu** [[00:44:07](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2647)]
That makes sense.

##### **Geohot** [[00:44:09](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2649)]
Yeah, so if we have a LLaMA 8b training, like, every day, we can start adding these tricks. We can definitely do gradient accumulation, modeling. We can start doing model splitting on LLaMA 8b. And then not worry about scaling up to 405b and not worry about performance. Just make sure that we have this thing training. It's MLPerf qualifying. And we start to add the tricks to it.

##### **Nimlgen** [[00:44:29](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2669)]
Yep, sounds good.

##### **Chenyu** [[00:44:33](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2673)]
I think once we validate and those flash attention works with the AK context, it's a pretty good progress. Then maybe just copy some of the, I don't know, the code. Have any. READINGS FROM Uh, RAM Putting

##### **Geohot** [[00:44:49](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2689)]
Was being Anyway awesome. Think I won't be running into problems with being

##### **Chrism** [[00:45:09](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2709)]
ally exhausting.

##### **Geohot** [[00:45:11](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2711)]
mentioned. maintenance check, something like that make getting months. PA verschiedene assignments from NOCA. PA something I really dig into. is this and GEMM and yes. So we have the SQTT timeline now. And for I think this week, I'm gonna add support to our reverse

##### **Qazalin** [[00:45:42](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2742)]
reverse engineers unpacker for CDNA. Currently, it's only works on our j three. I looked into a little a little bit for our journey for the packet structures different timestamps are different. It'll be fun to see what you think is out of it.

##### **Geohot** [[00:46:04](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2764)]
Yeah, cloud should be cloud should be pretty good at that.

##### **Qazalin** [[00:46:07](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2767)]
So all that we're on it. Spend an hour on this.

##### **Geohot** [[00:46:13](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2773)]
Yeah, I mean, you have to get it. So the way that I got this stuff for RDNA3 was I disassembled rocprof trace decoder in Ghidra. And then I pasted that C code into ChatGPT. Then I also did a bunch of GDB stuff to dump to jump the tables. I dumped all the stuff out of rocprof TraceDecoder. If you don't get this, like within like a day, don't spend a ton of time on it, because I can do it very quickly. I think it's more important that that you spend time on the on the visualization side of things, making sure that we can tie every packet back to an instruction. And then also things like making sure the barriers like right now, barriers just hard coded to have length 100 or whatever, making sure the barriers actually go to the end of the barriers. And then there's also the mystery of the wave ready packet. If you could figure out how to show those in a good way. But yeah, no, we've done that. We've done that. We've done that. We definitely need to add CDNA. But don't spend a ton of time on it. If you find yourself spending more than a day on it. I think I can do it really quickly.

##### **Geohot** [[00:47:55](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2875)]
I'll continue working on this stuff.

##### **Geohot** [[00:47:59](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2879)]
Yeah, no, I'm very happy with the yes, GTT tracelio. I think it's a I think it's a lot better than stall on instructions, which doesn't make any sense.

##### **Qazalin** [[00:48:09](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2889)]
Does not make any sense. Yeah, this one's like, I can see every single cycle.

##### **Geohot** [[00:48:14](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2894)]
Did you see my my work specialized stuff?

##### **Qazalin** [[00:48:18](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2898)]
Oh, yeah, the works are doing different colors. Yeah, you have different colors. See it?

##### **Geohot** [[00:48:26](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2906)]
Yeah, you can like like, I think that that's all you. Yeah, we should get this word for CDNA because we can lock I think that the one from is AMD is one work specialized. I think the one from the mojo is work specialized.

##### **Geohot** [[00:48:47](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2927)]
fast GEMM. Oh, the fast GEMM. I don't know. Honestly, I haven't heard that.

##### **Geohot** [[00:48:57](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2937)]
Um, be in a don't don't try a little with with with CDNA. But if it's like totally different. Yeah, I can do it real fast. But yeah, I want to be able to click on any uh, instruction either. Like we need to tie the exact to the the NQ.

##### **Geohot** [[00:49:25](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2965)]
Do you think it's actually possible to do it? Like, accurately? Of course, it's all in order. At least RDNA three is all in order.

##### **Geohot** [[00:49:42](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2982)]
So the order in which the NQ packets appear in the SQTT stream is the order in which the exact packets appear.

##### **Geohot** [[00:49:54](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=2994)]
Have you seen anything to think that's not true?

##### **Qazalin** [[00:50:06](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3006)]
No, I think that's true. I hope. Because otherwise, it would just be impossible. Like, it would be like modeling a CPU. No, you can't do that. Maybe GPU. Yeah.

##### **Geohot** [[00:50:19](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3019)]
Oh, well, yeah, I looked into trying to model cycle accurate stuff. I don't think that's gonna happen. There's a lot of there's a lot of noise. But I don't think that matters. But I think Yeah, I think it's all in order. So you can definitely tie them back together. It'll be great to be able to click. And then, yeah, see what's going on? And then also, eventually, we want this environment to be able to run the emulator. And in the emulator, we can see at any point, what?

##### **Geohot** [[00:50:58](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3058)]
What are all the actual values in the registers for?

##### **Qazalin** [[00:51:03](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3063)]
I see what an emulator with?

##### **Geohot** [[00:51:06](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3066)]
Wow, I mean, it just didn't make a request for like, what were the registers at this time stamp? But yeah. No, much less important. More important is to get these things reliably tied back to PC and then start using this to improve the speed of things. Yeah, spend a day on the CDNA thing. See if you can get it. But yeah, I think the right way to do it, did you see my test that compared it to rocprof TraceDecoder?

##### **Qazalin** [[00:51:38](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3098)]
I did, yeah, the SKTD examples.

##### **Geohot** [[00:51:42](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3102)]
Yeah, if you're just, what I would do, here's what I would do. Make a generator for those examples. I just generated those examples by hand, but make a script that auto regenerates the examples and add the same set of examples for CDNA, RDNA3, and RDNA4. And then, yeah, tell Claude to get them to pass for CDNA3 and RDNA4. See if you can do it.

##### **Qazalin** [[00:52:12](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3132)]
Yeah, I did this for RDNA4. I generated exactly the same things. It spends like two hours on it, and then just it's hopeless. I see. You'll see it.

##### **Geohot** [[00:52:27](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3147)]
But yeah, either way.

##### **Qazalin** [[00:52:30](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3150)]
Like it writes a lot of code and.

##### **Geohot** [[00:52:34](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3154)]
Yeah, no, it can't run. My experience with it is it can run for about two minutes autonomously without me having to. So I'm just going to say don't do that.

##### **Geohot** [[00:52:48](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3168)]
Superb. It's like, oh.

##### **Geohot** [[00:52:50](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3170)]
Yeah, like I'm pretty aggressively in the loop. But yeah, what would help me to work on this is if you write something to generate all those pickle examples and generate them for all three. And then add to that test and say, you know,

##### **Geohot** [[00:53:04](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3184)]
should work for CDNA, should work for RDNA4, but expected failure. Yeah. It sounds weird.

##### **Chrism** [[00:53:17](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3197)]
But I don't have time for that. Because I think people would learn much

##### **Geohot** [[00:53:17](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3197)]
Do you have anything related to running a fast sham in training? No. The current gerne only works for square matrices,

##### **Qazalin** [[00:53:34](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3214)]
and the bulk needs like any m and k. Hello.

##### **Geohot** [[00:53:41](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3221)]
What yougoldblk So, do you want to do that? Where do you get a GEMM from that only works for square matrices? Torch. How does Torch do not square matrices? Use other kernels. Hey.

##### **Geohot** [[00:54:01](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3241)]
It doesn't seem like a lot to ask. It doesn't seem like a lot to ask for to have a GEMM that supports rectangles.

##### **Qazalin** [[00:54:07](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3247)]
Yes, it is. I have a script for it. I have a, like, I can get the full dump of Torch. It will take me like an hour to get this.

##### **Geohot** [[00:54:17](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3257)]
All right, cool. Yeah, I think that's another good goal for the sprint. Because yeah, fast GEMMs is just free speed up for training. The other thing too, I saw you had a PR that's half done with the removing the MLPerf, having MLPerf just directly generate.

##### **Qazalin** [[00:54:40](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3280)]
Yeah, having the ELF directly generated. It's fully done. I mean, like, I upstream, I merged it, and then I merged master, and it broke. Yeah. Today I fixed it.

##### **Geohot** [[00:54:54](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3294)]
I can tell that some of that stuff's AI written. Just clean it up a little bit more.

##### **Qazalin** [[00:55:00](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3300)]
The ELF? No, that ELF is handwritten.

##### **Geohot** [[00:55:03](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3303)]
Oh, that's handwritten?

##### **Qazalin** [[00:55:05](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3305)]
That is handwritten, yeah. All right. All right.

##### **Geohot** [[00:55:09](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3309)]
OK. OK. Yeah, I think it could be cleaned up a bit more. It was just my, I thought that's why it wasn't merged.

##### **Qazalin** [[00:55:25](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3325)]
Feel free to comment on it. I don't see that.

##### **Geohot** [[00:55:29](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3329)]
No, I just thought that that's why it wasn't merged. I thought it was waiting for clean up to ELF.

##### **Geohot** [[00:55:41](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3341)]
OK. Oh, my god. This. Oh, wait. Never mind. Oh, this has changed. Yeah, this looks pretty good. Did you have an older one beforehand?

##### **Chrism** [[00:56:08](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3368)]
Yeah, I did.

##### **Geohot** [[00:56:12](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3372)]
I might have. Yeah, this looks pretty good. This is pretty minimal.

##### **Chrism** [[00:56:19](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3379)]
What's this supposed to be? Not CP-E. Not API? Not ECU. STORMFUL-? Well, we're fine.

##### **Geohot** [[00:56:38](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3398)]
I'm fine. Where's levant gıyoruz?

##### **Qazalin** [[00:56:39](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3399)]
fixes for CDNA DSL is in the same branch as my failing test. It's by Claude, but I reviewed it a lot. I think it's correct. Like it's some sort of like bit field issue with FP4 that you don't have four. You don't have seven SGPRs. You have four SGPRs or whatever.

##### **Chrism** [[00:57:04](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3424)]
I don't know if it's smaller.

##### **Geohot** [[00:57:10](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3430)]
Oh, one of those is wrong somehow?

##### **Geohot** [[00:57:13](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3433)]
I mean, I just pull all that from the XML files. There are some bugs in those files.

##### **Qazalin** [[00:57:19](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3439)]
Does the XML file describe based on a field, like based on a modifier, your register rate changes?

##### **Geohot** [[00:57:32](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3452)]
Oh, no. It just has the biggest one.

##### **Qazalin** [[00:57:35](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3455)]
Yeah, that's how FP4 works. Based on the modifier.

##### **Geohot** [[00:57:40](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3460)]
Got it. Yeah. Got it. Just. Yes. It's all in there. Cool. I'm wondering what I read before. Yeah, this looks good. The ELF pack looks good. I did. I just.

##### **Chrism** [[00:58:03](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3483)]
OK.

##### **Geohot** [[00:58:04](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3484)]
OK. Do you have anything on bounties? I don't think so. I don't remember. It's so frustrating now with all the AI crap.

##### **Geohot** [[00:58:38](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3518)]
I think every time there's a bounty that's like, I don't know. I mean, I think that there's people out there who just copy and paste the bounties into Cloud and say go. And then they did the easy part. The hard part is telling if it's good or not, which it probably isn't.

##### **Chenyu** [[00:58:54](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3534)]
I think on average, I get like 5% of the code, actual code. And just, yeah. For all other 95%. Why not? Overall. Her codex is good. I'm going to Thailand this week. It's a $20 tier first.

##### **Geohot** [[00:59:20](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3560)]
My friend did a study on whether AI makes her company more productive or not. And the end result was that there's no productivity change. I now see. I, you know, having. I'm not sure. I mean, having spent the last month using cloud aggressively, I see how it could potentially just make me less productive. The problem is you don't realize what you shouldn't be doing. You just go down a rabbit hole that you shouldn't go down and you don't really realize that because you're not doing it. It's not your effort being extended. It's like the very bottom line. It's the virtue of laziness.

##### **Geohot** [[01:00:11](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3611)]
Okay.

##### **Chenyu** [[01:00:14](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3614)]
Anyway, I think that's it for this meeting. Thank you, everyone. See you next week. Bye bye. Thanks.

##### **Geohot** [[01:00:21](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3621)]
Bye.

##### **Chrism** [[01:00:24](https://www.youtube.com/watch?v=vQY3NbmWoJw&t=3624)]
Bye.
