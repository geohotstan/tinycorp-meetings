# 2026-04-21 Meeting

### Meeting Agenda

**Time:** new meeting #16, 4/20 9pm Monday San Diego time
- company update
- new DEV
- MLPerf llama
- JIT refactor
- viz
- llm app, callify
- tensor UOp mixin
- bounties, issues, Comma happiness


### Audio

[Youtube Link](https://www.youtube.com/watch?v=12UzE2hXuGE)

### Highlights

- **[Chestnut launch priorities](#geohot-000059)**: Chestnut, the upcoming eGPU dock, is a near-term company priority, and the LLM app needs better prefill speed, tool calling, broader model support, and clearer JIT Beam status before launch.
- **[Close low-signal issues quickly](#geohot-000658)**: AI-written issues or PRs, and question-style issues, should be closed immediately so maintainers can focus on reproducible, high-signal bug reports.
- **[Make unsupported hardware explicit](#geohot-000750)**: RDNA2 is not supported, and the docs should say that clearly to set expectations and reduce avoidable issue traffic.
- **[Summer hardware push and launch prep](#geohot-001027)**: The team plans to start building the first Exa Box this summer, while focusing in San Diego on making the Chestnut launch successful and stress-testing the LLM app across a wide range of hardware.
- **[New DEV interface and mock GPU support](#chrism-001207)**: The new `dev` work now includes a mock GPU interface plus architecture- and flag-based CPU configuration, including a `native` mode that auto-detects available CPU features.
- **[Alias a default mock backend](#geohot-001814)**: `mock` should default to the simplest AMD mock path, likely `KFD`, so users can test GPU flows without needing to think through backend details.
- **[LLaMA memory regression in run linear](#wozeparrot-002156)**: A regression in `run linear` was traced to retained references preventing buffers from being freed between batches, and the proposed fix restores the old pop-based behavior.
- **[Fake-data profiling is misleading](#geohot-002457)**: NaNs in fake training data appear to take faster matmul paths and avoid normal power throttling, which means fake-data performance is overstating real LLaMA training speed.
- **[Agents should optimize kernels, humans should fix scheduling](#geohot-002925)**: The long-term vision is for agents to rewrite slow kernels automatically, while humans focus on harder non-convex problems like scheduling, copy overlap, and global optimization.
- **[JIT should precompile up front with progress reporting](#geohot-003351)**: Compilation and lowering should move into the graph rewrite so kernels are compiled up front, with visible progress and Beam status shown during execution.
- **[Viz CLI just landed](#chenyu-004036)**: A new `extra.viz.cli` tool was merged, allowing users to reconstruct and inspect debug output directly from the command line.
- **[Replicate the Kimi-style autonomous optimization loop](#geohot-004823)**: The next big viz goal is to support a 12-hour autonomous agent loop on RDNA3 hardware that can keep improving kernels over time, similar to the Kimi graph.
- **[LLM app is becoming part of tinygrad itself](#geohot-005441)**: The LLM app was moved into the `llm` directory, with dequant moving into loaders, reflecting the view that LLM tooling is becoming core tinygrad infrastructure.
- **[Comma should not require internet access](#geohot-010412)**: Downloading AMD firmware at runtime is a problem for Comma use cases, and the team wants a solution that works offline without relying on the internet.

### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=12UzE2hXuGE&t=0)]
Great. So next week meeting will be Tuesday. Also flip back to, because no one will be in Hong Kong, so no more Hong Kong time. Then back to Monday, the week after that. And we can start with company update.

##### **Geohot** [[00:00:27](https://www.youtube.com/watch?v=12UzE2hXuGE&t=27)]
Yes, I think two things.

##### **Geohot** [[00:00:28](https://www.youtube.com/watch?v=12UzE2hXuGE&t=28)]
One is we have some product launches in the pipeline. We have the one that we've talked about a little and the one that we haven't talked about at all. Those are exciting. The other thing is if you search for Tinygrad now on YouTube, there's a lot of videos.

##### **Chenyu** [[00:00:52](https://www.youtube.com/watch?v=12UzE2hXuGE&t=52)]
Is it the same or similar thing to the previous one?

##### **Geohot** [[00:00:59](https://www.youtube.com/watch?v=12UzE2hXuGE&t=59)]
Kind of. It's things like this. There's Korean ones, there's Japanese ones. That has like 65,000 views. So we're getting a lot of people in. Now, I don't know if any of these people are going to be any good and are going to be contributors or anything. But there's a lot of excitement around this. And then, yeah. But the product launch, we have talked about it. It's the Chestnut, which is our eGPU dock. I want to make sure by the time we launch that, that the LLM app is pretty decent. So I think it's important that we do that. We have to fix the pre-fill speed. We have to add tool calling support. We have to make sure it supports all the models people care about. I think the overall speed is pretty good. But we have to make it clear to people they have to use JIT Beam. We should have better status updates during JIT Beam. Maybe we could do a pass on Beam itself and make it faster. But yeah, I think this is pretty high priority for the company. This is how we're going to get a lot of people using TinyGrad. This is the first use case, right? There's only going to be more of these that come.

##### **Chenyu** [[00:02:17](https://www.youtube.com/watch?v=12UzE2hXuGE&t=137)]
I think we can discuss about, because of this recent surge of users trying TinyGrad, there are also lots of issues. We can discuss this at the end. But I think we can talk about it at the end of the meeting to see how we want to handle these.

##### **Geohot** [[00:02:32](https://www.youtube.com/watch?v=12UzE2hXuGE&t=152)]
Oh, I haven't even looked at issues.

##### **Chenyu** [[00:02:35](https://www.youtube.com/watch?v=12UzE2hXuGE&t=155)]
There are a bunch of things people try in different combinations of the boards and the GPUs. And sometimes it fails with weird errors and things like that.

##### **Geohot** [[00:02:45](https://www.youtube.com/watch?v=12UzE2hXuGE&t=165)]
Interesting. I mean, again, I think a lot of it is we shouldn't really be. We should really only support our external GPU dock. It hasn't launched yet. But I think what we're going to say is, like, because a lot of this is, like, weird broken docks and bad cables and stuff.

##### **Chenyu** [[00:03:03](https://www.youtube.com/watch?v=12UzE2hXuGE&t=183)]
I think it's more of a we just need to decide what we want to do and not having those issues hanging forever.

##### **Geohot** [[00:03:10](https://www.youtube.com/watch?v=12UzE2hXuGE&t=190)]
Yeah. I almost wish there was just a way to put them in a big folder. Anything that looks like AI wrote the issue or AI wrote the pull request, I'm done even reading these. I just write in all caps, do not use AI and close them. Like, anybody who actually is so good at this stuff, like, I'm going to go ahead so lazy that they didn't. It's bad enough if they I wrote the code. But the fact that I then wrote the pull request, that's just a bar of like, no, definitely not.

##### **Geohot** [[00:03:39](https://www.youtube.com/watch?v=12UzE2hXuGE&t=219)]
How many of these have the dumbass, like, Claude hook to them? That's for you, I think. Okay.

##### **Geohot** [[00:03:56](https://www.youtube.com/watch?v=12UzE2hXuGE&t=236)]
Okay, so here's an issue that I think should just be closed. This is not an issue.

##### **Chenyu** [[00:04:02](https://www.youtube.com/watch?v=12UzE2hXuGE&t=242)]
Oh yeah, so those are questions. And usually what I deal with questions is move it to discuss

##### **Geohot** [[00:04:07](https://www.youtube.com/watch?v=12UzE2hXuGE&t=247)]
and it will be forgotten forever. Yeah, I think questions can just be closed.

##### **Chenyu** [[00:04:13](https://www.youtube.com/watch?v=12UzE2hXuGE&t=253)]
That's not an issue, right? Yeah, so those will close, right? But

##### **Geohot** [[00:04:17](https://www.youtube.com/watch?v=12UzE2hXuGE&t=257)]
there are kind of issues. And now we have, like here, this one circular import error. We have this issue. That's written by AI. Do not use AI.

##### **Geohot** [[00:04:36](https://www.youtube.com/watch?v=12UzE2hXuGE&t=276)]
Where do people get this template from? This is some AI crap.

##### **Chenyu** [[00:04:45](https://www.youtube.com/watch?v=12UzE2hXuGE&t=285)]
That's AI.

##### **Geohot** [[00:04:50](https://www.youtube.com/watch?v=12UzE2hXuGE&t=290)]
Oh yeah, with the AI. Without a doubt.

##### **Chenyu** [[00:04:56](https://www.youtube.com/watch?v=12UzE2hXuGE&t=296)]
You're saying there's no circular import if I try?

##### **Geohot** [[00:05:00](https://www.youtube.com/watch?v=12UzE2hXuGE&t=300)]
I don't know if there's a circular import, but again, my point is no human wrote this, right? You can see the use of the m-dash. You can see the use of the... Yeah, I mean, it's AI, right? You think a human wrote those arrows? Which cascades through? Come on, no human wrote that. Yeah, probably. And then you can also, you can always click on the person's GitHub and take a look and, oh, it's their first issue. Great. Like, no. Right, like we're not here to do customer support for people. We're here to just close all the low signal shit. People shouldn't be putting an issue... People should be putting... Now let's, you know what? Let's contrast this to good issues. Let's contrast this to the ones that are that... Right.

##### **Geohot** [[00:05:52](https://www.youtube.com/watch?v=12UzE2hXuGE&t=352)]
Right. Like, this is a good issue. Right. So we can tell it's clearly not written by AI. It has a repro. It has a suggested patch. Actually, is that already fixed? Oh, it's already fixed.

##### **Chrism** [[00:06:15](https://www.youtube.com/watch?v=12UzE2hXuGE&t=375)]
But I feel like this issue may crop up in other areas. Like, this feels like... You know, like, that happened to fix it, but I didn't close it because I was like... It seemed like this might be a bigger issue. Like, this specific repro doesn't...

##### **Geohot** [[00:06:32](https://www.youtube.com/watch?v=12UzE2hXuGE&t=392)]
I think the CloudFix is largely correct. You just need to make sure when you pickle it creates new unique.

##### **Chrism** [[00:06:39](https://www.youtube.com/watch?v=12UzE2hXuGE&t=399)]
Yeah, it's mostly correct. I think if you... So if you were to pickle... If you were to pickle two objects containing the same unique and then load them both in the same... Like, and then load them both as separate units, then you would have to pick them separately. And so that means if we had separate things in a different process and they would be different uniques.

##### **Geohot** [[00:06:58](https://www.youtube.com/watch?v=12UzE2hXuGE&t=418)]
We can get to the specifics of this later. But just to talk about, like, what good issues are and what bad issues are, anything that's AI or a question should just be

##### **Geohot** [[00:07:08](https://www.youtube.com/watch?v=12UzE2hXuGE&t=428)]
immediately closed. Same thing with the PRs.

##### **Chenyu** [[00:07:18](https://www.youtube.com/watch?v=12UzE2hXuGE&t=438)]
Yeah. Okay.

##### **Geohot** [[00:07:20](https://www.youtube.com/watch?v=12UzE2hXuGE&t=440)]
Still, we will...

##### **Chenyu** [[00:07:21](https://www.youtube.com/watch?v=12UzE2hXuGE&t=441)]
...we're off to... There are some of the, I think most of this Mac and some kind of GPU, we still need to find a way to deal with those.

##### **Geohot** [[00:07:32](https://www.youtube.com/watch?v=12UzE2hXuGE&t=452)]
Well, I mean, some of the, yeah, I agree. And if we can find something that we can actually reproduce, then let's do it. But here's an issue with RDNA2.

##### **Chenyu** [[00:07:46](https://www.youtube.com/watch?v=12UzE2hXuGE&t=466)]
RDNA2 is not supported. We can say we don't support it.

##### **Geohot** [[00:07:50](https://www.youtube.com/watch?v=12UzE2hXuGE&t=470)]
So NimbleGen, I see you replied to that. Just when you reply to it, just close the issue. RDNA2 is not supported. And I think we should update our doc to make sure that that's clear.

##### **Geohot** [[00:08:00](https://www.youtube.com/watch?v=12UzE2hXuGE&t=480)]
Like some of this stuff needs to just be setting expectations for people.

##### **Geohot** [[00:08:12](https://www.youtube.com/watch?v=12UzE2hXuGE&t=492)]
Yeah, no, I mean, yeah. I don't know if we can like, I've seen some Git Hubs that have like. I've seen some Git Hubs that have like, I've seen some Git Hubs that just turn issues off entirely. I don't think that's the right idea. But if we can put some like banner on top of issues, saying like questions will be closed without comment, anything that's written by AI will be closed without comment.

##### **Chenyu** [[00:08:33](https://www.youtube.com/watch?v=12UzE2hXuGE&t=513)]
I don't think those banner really stop people from posting AI stuff. No, it's not going to stop. If you're capable to read banners, I think you will have more social capability.

##### **Geohot** [[00:08:47](https://www.youtube.com/watch?v=12UzE2hXuGE&t=527)]
No, no, no, no. But the point of the banner is not to stop people from posting AI slop. It's just to communicate to everybody, mostly even here, that that's our policy about AI slop, right? It's not about stopping people from posting AI slop. It's just so like, the thing about AI slop is like, it's not actually that bad as long as you immediately identify it and click close on the issue. You can deal with this all in seconds. But if you have to spend time, you're going to have to do it. If you have to spend time and you read it, and you treat it like it might be something real, then they got you. A machine is wasting your time.

##### **Chenyu** [[00:09:28](https://www.youtube.com/watch?v=12UzE2hXuGE&t=568)]
It's never a machine wasting your time, right? It's another human wasting your time.

##### **Chenyu** [[00:09:32](https://www.youtube.com/watch?v=12UzE2hXuGE&t=572)]
Wow.

##### **Chenyu** [[00:09:32](https://www.youtube.com/watch?v=12UzE2hXuGE&t=572)]
No human using the machine. OK, anyway.

##### **Geohot** [[00:09:37](https://www.youtube.com/watch?v=12UzE2hXuGE&t=577)]
Sure, sure, sure.

##### **Chenyu** [[00:09:41](https://www.youtube.com/watch?v=12UzE2hXuGE&t=581)]
Anyway, another thing is because these hanging issues were likely to like,

##### **Chenyu** [[00:09:53](https://www.youtube.com/watch?v=12UzE2hXuGE&t=593)]
agree. That's another reason I don't like these hanging around.

##### **Wozeparrot** [[00:09:57](https://www.youtube.com/watch?v=12UzE2hXuGE&t=597)]
Yeah.

##### **Chenyu** [[00:09:58](https://www.youtube.com/watch?v=12UzE2hXuGE&t=598)]
OK, we will see. I think as we have more adoptions, we will get just to some of these.

##### **Geohot** [[00:10:05](https://www.youtube.com/watch?v=12UzE2hXuGE&t=605)]
I went to a pull request yesterday.

##### **Geohot** [[00:10:07](https://www.youtube.com/watch?v=12UzE2hXuGE&t=607)]
We have a lot less pull requests.

##### **Chenyu** [[00:10:09](https://www.youtube.com/watch?v=12UzE2hXuGE&t=609)]
Great. Yeah.

##### **Geohot** [[00:10:14](https://www.youtube.com/watch?v=12UzE2hXuGE&t=614)]
OK, sounds good. So wait, what?

##### **Chenyu** [[00:10:20](https://www.youtube.com/watch?v=12UzE2hXuGE&t=620)]
OK, let's move on. Oh, that's it? That's it? All for company update?

##### **Geohot** [[00:10:27](https://www.youtube.com/watch?v=12UzE2hXuGE&t=627)]
I think so, yeah. Going to start building out the Exa Box this summer. Build out the first Exa Box. We've got to make sure the eGPU is good for Comma and good for our use. Yeah, I mean, so I'm back in San Diego in May. The main thing that I want to do is just make sure that our Chestnut launch goes well. I want to make the LLM app more usable. And then I want to test it on a large variety of hardware and really stress it. We have every GPU. We have every USB 4 port, every USB 3 port.

##### **Geohot** [[00:11:02](https://www.youtube.com/watch?v=12UzE2hXuGE&t=662)]
We just need to test all this stuff.

##### **Qazalin** [[00:11:09](https://www.youtube.com/watch?v=12UzE2hXuGE&t=669)]
Good.

##### **Chenyu** [[00:11:13](https://www.youtube.com/watch?v=12UzE2hXuGE&t=673)]
OK.

##### **Qazalin** [[00:11:14](https://www.youtube.com/watch?v=12UzE2hXuGE&t=674)]
Wow. Wow.

##### **Geohot** [[00:11:14](https://www.youtube.com/watch?v=12UzE2hXuGE&t=674)]
I also think we're going to sell. We're going to sell a lot of these. Right? Like, look at all the people who watch these YouTube videos. And we're pricing it at a price point where it's the kind of thing that people are just going to click Buy on without thinking too much about it.

##### **Geohot** [[00:11:34](https://www.youtube.com/watch?v=12UzE2hXuGE&t=694)]
The beauty of $200 is people just click Buy. Like my rabbit? Exactly.

##### **Geohot** [[00:11:42](https://www.youtube.com/watch?v=12UzE2hXuGE&t=702)]
Exactly. It was $200. So you just click Buy. You don't use it. You just click Buy.

##### **Chenyu** [[00:11:51](https://www.youtube.com/watch?v=12UzE2hXuGE&t=711)]
OK. Great. Anyway, let's move on. Let's start with actual items. The first one, I just reversed from the last time. So first one, let's start with the new dev. Chris.

##### **Qazalin** [[00:12:03](https://www.youtube.com/watch?v=12UzE2hXuGE&t=723)]
OK.

##### **Geohot** [[00:12:06](https://www.youtube.com/watch?v=12UzE2hXuGE&t=726)]
Yeah.

##### **Chrism** [[00:12:07](https://www.youtube.com/watch?v=12UzE2hXuGE&t=727)]
So yeah. So yeah. So there's not all that many changes to dev now that it's kind of mostly solidified. Mock GPU interface. And I started moving some stuff to actually use arch. So you can now specify all of your feature flags in CPU, which is kind of cool. So the way that works is you're going to specify the architecture, but then you also specify the CPU that you want to do your tuning for. And then you specify the flags. And then you can just put `native`. And then if you put `native`, then it'll just figure out for you what you have available. Do we have docs on this anywhere? Yeah. Sorry. I should write docs for that. There are hopefully useful error messages, but I will document that as well.

##### **Geohot** [[00:13:08](https://www.youtube.com/watch?v=12UzE2hXuGE&t=788)]
All right. So this is for things like AMX.

##### **Chrism** [[00:13:13](https://www.youtube.com/watch?v=12UzE2hXuGE&t=793)]
For right now, it's just for like AVX or AVX2 or AVX512. But I will put AMX in there as well.

##### **Qazalin** [[00:13:18](https://www.youtube.com/watch?v=12UzE2hXuGE&t=798)]
And that's going to do it for now.

##### **Chrism** [[00:13:18](https://www.youtube.com/watch?v=12UzE2hXuGE&t=798)]
But I will put AMX in there as well. There's some sort of question about, OK, well, do you want to make AMX on by default? Because changing it is then now a little bit annoying. So if you want it to be the non-default value, it's a little bit verbose to change it compared to just saying, like, AMX equals 1.

##### **Geohot** [[00:13:39](https://www.youtube.com/watch?v=12UzE2hXuGE&t=819)]
I mean, we want to get rid of all of these flags, right? Most of the point of the dev project is just to kill off all of the hidden environment variables. Yeah. So I mean, I think the way to do it, yeah, sure, it could be on by default, but you just want something like minus AMX or something.

##### **Chrism** [[00:13:56](https://www.youtube.com/watch?v=12UzE2hXuGE&t=836)]
Yeah, yeah, yeah. Yeah, that's the way it would look. The only thing that's worth pointing about AMX is that AMX also refers to some other thing for Intel, which is a little bit confusing. Yeah. I'm fine with calling it Apple AMX or something. Yeah, yeah, Apple AMX. Also like all caps AMX also would work. Anyway, I don't know.

##### **Geohot** [[00:14:20](https://www.youtube.com/watch?v=12UzE2hXuGE&t=860)]
Speaking of all caps, so I just read the CPU renderers use arch thing. The CPU arch is all capital `ARM64` on the Qualcomm Windows computer. But just add a `.lower()`. Yeah, just make sure that's canonicalized. I see like AMD GPUs in caps. So if you just do `arch.lower()` and yeah.

##### **Chrism** [[00:14:47](https://www.youtube.com/watch?v=12UzE2hXuGE&t=887)]
Yeah, yeah, yeah. Sorry, I didn't I didn't realize. It's like different on every machine. It's kind of annoying.

##### **Geohot** [[00:14:54](https://www.youtube.com/watch?v=12UzE2hXuGE&t=894)]
Yeah, I was testing and the Windows one has bugs too. I posted about this and Oh, yeah. But but yeah, but regardless, yeah, that was that was the only actual bug I had to fix to get it to run.

##### **Qazalin** [[00:15:07](https://www.youtube.com/watch?v=12UzE2hXuGE&t=907)]
Okay.

##### **Geohot** [[00:15:11](https://www.youtube.com/watch?v=12UzE2hXuGE&t=911)]
Well, and then yeah, how much more so does mock work?

##### **Chrism** [[00:15:15](https://www.youtube.com/watch?v=12UzE2hXuGE&t=915)]
Yeah, mock works. So you put, you know, `mock+PCI` or `mock+KFD` or `mock+USB` on AMD, or on NVIDIA you can put `mock+NVK`.

##### **Geohot** [[00:15:31](https://www.youtube.com/watch?v=12UzE2hXuGE&t=931)]
Okay, so mock. So just dev equals mock PCI. Yeah. And then I'll just say test tiny. Okay, this failed because there's no module named test. Any Python path. No, I'm seeing all kinds of crap about it seems on this is probably unrelated, but that's

##### **Geohot** [[00:15:58](https://www.youtube.com/watch?v=12UzE2hXuGE&t=958)]
the area when you do that. Oh, yeah, it's fine.

##### **Chrism** [[00:16:06](https://www.youtube.com/watch?v=12UzE2hXuGE&t=966)]
This is I think I thought someone opened a PR about this or maybe an issue. We should just we just need to suppress warnings in Dell. I think I think there's a PR open for this that does this.

##### **Qazalin** [[00:16:18](https://www.youtube.com/watch?v=12UzE2hXuGE&t=978)]
Right?

##### **Geohot** [[00:16:19](https://www.youtube.com/watch?v=12UzE2hXuGE&t=979)]
Probably, yeah, otherwise `mock+PCI+AMD` works. What does `mock+USB` do? Yeah.

##### **Geohot** [[00:16:31](https://www.youtube.com/watch?v=12UzE2hXuGE&t=991)]
I see. Um, should there be a default mock? Oh, yeah.

##### **Chrism** [[00:16:38](https://www.youtube.com/watch?v=12UzE2hXuGE&t=998)]
I mean, it's kind of unclear what you want. I thought about this, but I kind of felt like it was better to be more explicit.

##### **Geohot** [[00:16:47](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1007)]
But well, yeah, okay, I guess that's fine. I mean, because normally you're putting a Yeah, that's fine for now.

##### **Qazalin** [[00:16:57](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1017)]
Yeah.

##### **Chrism** [[00:16:58](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1018)]
Oh, yeah, there's also a `mock+CUDA`, which you just put `mock+CUDA` and then that does the GPUOcelot.

##### **Geohot** [[00:17:05](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1025)]
Oh, so it's mock. So it's just mock plus CUDA.

##### **Chenyu** [[00:17:08](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1028)]
Yeah.

##### **Geohot** [[00:17:12](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1032)]
Okay, so I'm getting that doesn't work for me, I get invalid value for GPU architecture.

##### **Chenyu** [[00:17:23](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1043)]
Oh, wait.

##### **Chrism** [[00:17:25](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1045)]
If you're running on the same computer, it says you couldn't find `libgpuocelot`, although that is not a good error message.

##### **Geohot** [[00:17:33](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1053)]
Well, I mean, that's I don't even think that's what the problem is here.

##### **Chrism** [[00:17:39](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1059)]
All right, I will I'll take a look.

##### **Geohot** [[00:17:42](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1062)]
My guess is the problem here is that I have a version of CUDA that's too new to support them. Oh, yeah, yeah, yeah, yeah, you're right. Um, or, yeah, for AMD, I mean, I kind of would like there to be a default mock. Is it easy to just alias `mock+PCI` as the default mock, or `mock+KFD`, whatever the whatever the

##### **Geohot** [[00:18:02](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1082)]
like, because it doesn't.

##### **Geohot** [[00:18:04](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1084)]
Yeah.

##### **Geohot** [[00:18:04](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1084)]
Like, what's the simplest mock?

##### **Chrism** [[00:18:10](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1090)]
Uh, I guess it's, I think it's `KFD`. I think `KFD` is the simplest one.

##### **Geohot** [[00:18:14](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1094)]
Yeah, then just alias that.

##### **Chrism** [[00:18:16](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1096)]
Yeah, yeah, I need that.

##### **Geohot** [[00:18:18](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1098)]
Whichever. Yeah, whichever.

##### **Geohot** [[00:18:19](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1099)]
It seems like it runs the fastest. Great.

##### **Qazalin** [[00:18:21](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1101)]
Yeah.

##### **Chrism** [[00:18:24](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1104)]
Um, what else?

##### **Geohot** [[00:18:25](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1105)]
Yeah, because I would, I just want it, I expect that mock plus to be able to work without having to think about like, you know, what, what is the mark for?

##### **Chrism** [[00:18:34](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1114)]
Yeah, that makes sense. Yeah.

##### **Geohot** [[00:18:37](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1117)]
But no, I mean, it's great. It's great that like, this is now a simple way for everybody who doesn't have the GPU to basically test the entire flow of that GPU.

##### **Chenyu** [[00:18:48](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1128)]
Yeah.

##### **Chrism** [[00:18:52](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1132)]
What else? Yeah, so the other thing, I guess we can talk about this more probably later if we're gonna talk about JIT stuff changes, but definitely run into some regressions. Yeah. So, um, so I think one of the things here, especially, so if you load a pickled jitted function now, it recompiles everything. And for one, this broke no locals. So if you have a no locals function, and you jit it, and then you pickle that jit, and then you load it in a separate process, the no locals optimization will no longer be applied. There's that. And then also just this is confusing. Maybe, maybe it's correct, but we still should probably have a way of being able to save functions that are compiled such that you can load them later, because there's definitely a feature that Comma wants to have.

##### **Geohot** [[00:19:50](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1190)]
Oh, let's see. Yeah. So this is the like linear jet stuff causing these. Yeah. Yeah. But we can talk about that later. That maybe is not.

##### **Chenyu** [[00:20:03](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1203)]
Right now. Yeah.

##### **Chrism** [[00:20:07](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1207)]
So, um, yeah, other things are, uh, num GPUs. I'm adding this, but it's going to be like a `.count`. Um, that also makes it easier to put nicer error messages that aren't just like list index out of range.

##### **Chenyu** [[00:20:22](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1222)]
Um, should be good.

##### **Geohot** [[00:20:28](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1228)]
Uh, so it's going to be like `Device["AMD"].count`.

##### **Chrism** [[00:20:32](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1232)]
Uh, yeah.

##### **Geohot** [[00:20:34](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1234)]
Yeah. That's it.

##### **Chrism** [[00:20:37](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1237)]
Um, and then the other thing that's worth pointing out there is like right now we don't support multiple USB GPUs, but I think there's not really any reason that we couldn't, um, we just have to actually traverse the tree using `libusb` as opposed to just doing like, you know, get the first one.

##### **Geohot** [[00:20:54](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1254)]
Well, yeah, no, I mean, I think those are important things to support, uh, before we

##### **Geohot** [[00:20:58](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1258)]
launch Chestnut. Yeah. Make sure.

##### **Qazalin** [[00:21:01](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1261)]
Okay. Okay. Yeah. Cool.

##### **Chrism** [[00:21:06](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1266)]
I think that's it.

##### **Geohot** [[00:21:07](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1267)]
Um, if there's anything else that, that, uh, that people are upset about with respect

##### **Chrism** [[00:21:13](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1273)]
to dev, let me know, but yeah.

##### **Chenyu** [[00:21:21](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1281)]
Sounds good.

##### **Chenyu** [[00:21:27](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1287)]
Oh, we might want to also update the `python -m tinygrad.device` thing. Oh yeah. Yeah. Yeah. Yeah. We'll do that.

##### **Chrism** [[00:21:36](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1296)]
Yeah. Interface is when we get out of that and, uh, that, that happens.

##### **Geohot** [[00:21:45](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1305)]
Next is llama. Um, run linear also regressed something for llama.

##### **Wozeparrot** [[00:21:56](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1316)]
Uh, I have a PR that fixes it. Basically, the linear holds reference to all the calls, and then this just doesn't free anything between batches.

##### **Qazalin** [[00:22:12](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1332)]
So this won't have any side effects.

##### **Geohot** [[00:22:13](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1333)]
Oh yeah. I mean, this has always been a subtle bug where this is why, like, if you read the old `ExecItem` code, it would pop things off the list.

##### **Chenyu** [[00:22:33](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1353)]
How's that? Why's that?

##### **Wozeparrot** [[00:22:34](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1354)]
PR basically matches the old behavior of popping the calls.

##### **Geohot** [[00:22:40](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1360)]
Yeah, I think that's probably fine, right?

##### **Geohot** [[00:22:44](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1364)]
Like, yeah, so I see what it is now. Like, at the end of `realize.py`, you have the call in linear source. Yeah.

##### **Geohot** [[00:22:52](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1372)]
Yeah, I mean, you're passing in linear as the UOP.

##### **Geohot** [[00:22:55](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1375)]
You want buffers to be freed? Yeah. The solution probably isn't to delete the UOP. The solution is probably to free the buffers.

##### **Geohot** [[00:23:11](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1391)]
Explicitly free the buffers? Yeah, probably.

##### **Chenyu** [[00:23:19](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1399)]
I don't know. Annoying.

##### **Geohot** [[00:23:26](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1406)]
I don't know, but yeah, that's been, there could have been better regression tests for that

##### **Geohot** [[00:23:30](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1410)]
because that's a known problem. Maybe NimbleGen has ideas about how to, like, fix it.

##### **Geohot** [[00:23:41](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1421)]
But yeah, we'll get to that. How's LLaMA going otherwise?

##### **Wozeparrot** [[00:23:45](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1425)]
We saved another 30 minutes. It's getting much harder to find places to save because now all the kernels are fairly fast. I guess there's mostly just kind of the long tail to top, but it's very, very hard to find the long tail. I think it's getting clear what a lot of the long tail is doing and whether or not changing stuff there actually saves time.

##### **Geohot** [[00:24:12](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1452)]
Well, so how much will be fixed when we fix the linear regression?

##### **Wozeparrot** [[00:24:22](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1462)]
Linear regression just speeds up eval because I can work around the linear regression by dropping eval BS to eight.

##### **Geohot** [[00:24:32](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1472)]
I see. Yeah. I mean, yeah, we should probably even free the whole.

##### **Geohot** [[00:24:36](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1476)]
We should be more aggressive in general about just, like, freeing things in between jets, and it should hit the LRU cache. We'll talk about that when we talk about jet. So what is this? What is this long tail? Are there still an absurd amount of copies happening? And how come you said, what, three hours? And now we're back to...

##### **Wozeparrot** [[00:24:57](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1497)]
So this is the whole NaN being fake performance? This is the whole thing that I've found? Seems like NaNs take a faster path out during matmuls, but we don't hit PPT power throttling if we train with fake data, because it's all NaN.

##### **Geohot** [[00:25:19](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1519)]
Oh, we make the fake data not NAN?

##### **Wozeparrot** [[00:25:25](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1525)]
Uh, yeah, I think so. The problem is we have to make the weights not NaN. And currently, we're not doing that. Currently, the weights for fake data, we just assign `Tensor.empty`.

##### **Chenyu** [[00:25:40](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1540)]
Oh, let me see.

##### **Geohot** [[00:25:48](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1548)]
Yeah, how fast is it trying to collect that? We can have some legit init, no?

##### **Chenyu** [[00:25:54](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1554)]
Is it fast? Yeah.

##### **Chenyu** [[00:26:00](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1560)]
My proposal was, you can certainly try the same init weights that's legit, and having like a very small... very small learning rate, yeah... to just, if you want to, just test this hypothesis.

##### **Geohot** [[00:26:19](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1579)]
I mean, yeah, we should figure out... I want the profiler to be actually reflective of what's really going on. Yeah. I don't know. I mean, it looks like there's still a lot of slow kernels. What's the latest in the profiler? The latest in the profiler?

##### **Chenyu** [[00:26:34](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1594)]
Uh... We're... At... I guess I've been using my profiler. We're at this...

##### **Geohot** [[00:26:48](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1608)]
Why are you using your profiler and not the other one? This basically just splits it by category.

##### **Chenyu** [[00:26:59](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1619)]
Let's see... Yeah.

##### **Wozeparrot** [[00:27:03](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1623)]
Let's see. So, let's see if it's a little more obvious to me when I'm visually looking at it. You see that what is slow.

##### **Geohot** [[00:27:10](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1630)]
I mean, we'll talk about this when we talk about viz, but...

##### **Chenyu** [[00:27:18](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1638)]
Okay.

##### **Geohot** [[00:27:19](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1639)]
So, the step time is 1.5... 1.7 seconds. Uh...

##### **Geohot** [[00:27:31](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1651)]
So, you break down copy. Shouldn't all the copy be overlapped? Is that overlapped copy or non-overlapped copy?

##### **Wozeparrot** [[00:27:37](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1657)]
This is non-overlapped copy.

##### **Geohot** [[00:27:42](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1662)]
Oh... Why is all the copy not overlapped?

##### **Wozeparrot** [[00:27:45](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1665)]
This is not all a copy. This is explicitly the non-overlapped copy. There is copy that is overlapped. There's a lot of copy that is overlapped.

##### **Geohot** [[00:27:54](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1674)]
I see. I mean, why is all the copy not overlapped? This is data parallel. Yeah.

##### **Wozeparrot** [[00:28:00](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1680)]
I guess all the copy should be overlapped.

##### **Geohot** [[00:28:03](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1683)]
All the copy should be overlapped.

##### **Geohot** [[00:28:08](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1688)]
Well, okay. So... What's the total number of steps we got, though?

##### **Wozeparrot** [[00:28:16](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1696)]
6,250.

##### **Geohot** [[00:28:19](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1699)]
6,250 seconds to the app. Somewhere around there. So, that's 3.04 hours if you go with that timer. Okay. So, I'm sure that's about right. We're going to have to do just the flash attention. So, we're not going to make the gem of the flash attention faster. I think that's just what it is.

##### **Geohot** [[00:28:39](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1719)]
So, if we're doing just the gem of the flash attention, we're looking at 1.5 hours. So, we got to fix this other crap. So, we're going to have to fix this other crap.

##### **Wozeparrot** [[00:29:02](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1742)]
There's a lot of kernels in other, but also a lot of them are real kernels.

##### **Geohot** [[00:29:08](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1748)]
Well, so I see you say this `fused_silu_mulcast_amax_w13`. What is that? Where's that name coming from?

##### **Wozeparrot** [[00:29:16](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1756)]
I don't know if this one's in master. I'm on a different branch where I'm just testing a bunch of stuff.

##### **Geohot** [[00:29:25](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1765)]
Well, the way that I'd really like to deal with these other kernels is I want some agentic loop to just do it.

##### **Wozeparrot** [[00:29:31](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1771)]
Yeah, that's basically what I've been doing.

##### **Geohot** [[00:29:33](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1773)]
Yeah, yeah, yeah, yeah. So I want this stuff to be fast enough. Hopefully, I mean, we're talking about viz next. This is the main thing I want to talk about. I think that there is nothing fundamental about these other kernels. And what I want to do, what I want everyone, this is kind of related to dev stuff too, I want to make sure this is related to dev stuff, this is related to JIT stuff. I want to make sure that agents are capable of replacing stuff with hand-coded kernels pretty easily. Because I think the solution to this isn't for us to start writing each one of these kernels. It's to have agents come in and just, oh, well, okay, yeah, I'll rewrite that as this, I'll rewrite that as this, I'll rewrite that as this, boom. And then, but the copy thing, agents aren't going to be able to fix. Like I don't understand why they do this. That we have to fix ourselves. Yeah, we want the APIs to be really good and simple and predictable, such that agents can come in and make all those other kernels fast. Also, if we still have a lot of useless copies, we should figure out why `rangeify` is not optimizing them out, which is another thing that agents aren't going to do. But what we should be able to trust agents to do are to make kernels fast. Like the end solution, when I talk on Twitter about how TinyGrad is going to be 25,000 lines and have beyond state-of-the-art performance, look at that Kimi graph. This is how we're going to do it. We're not going to do all of the time that humans have spent on stupid heuristics over and over again to try to make these things fast. And that's what all of the millions of lines of CUDA and HIP are and stuff. It's all repetitive. It's all going to be replaced by AI. It's all going to be replaced by exactly what that agentic loop did. But the things that AI will never ever be able to do is scheduling at a grand scale. That's the kind of problem they're just not good at. They probably will never be good at because it's the other kind of... The reason the LLM inference thing worked the way it does is because it's a convex search problem. If you make the problem a convex search problem, AI is very, very good at it. If you make the problem a, well, you have to actually uncover this new thing and you have to try down this route for a bit, then it'll never figure it out. Or to say what Terence Tao said, he said, AI can jump, it can't climb.

##### **Geohot** [[00:32:18](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1938)]
So, yeah, we have to make sure that our APIs are really clean for agents to come in and write all that. All right.

##### **Chenyu** [[00:32:41](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1961)]
So, let's start with JIT first. Yeah, so for the compile issue, yeah, it's possible to fix.

##### **Nimlgen** [[00:33:00](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1980)]
I just thought that maybe we want to have this JIT capture to be portable. But basically, the solution here is to decouple `get_program`, actually just compile things into the program.

##### **Geohot** [[00:33:18](https://www.youtube.com/watch?v=12UzE2hXuGE&t=1998)]
I'm okay with you making the change to where it does all the compilation up front.

##### **Chenyu** [[00:33:28](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2008)]
Yeah, okay.

##### **Geohot** [[00:33:30](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2010)]
Like, I know right now it's still doing the compilation.

##### **Geohot** [[00:33:36](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2016)]
I'm going to do the compilation one at a time. Right, like, in exec kernel, it's calling `get_runner`. We should do all of that up front, right?

##### **Geohot** [[00:33:43](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2023)]
That should actually be part of the rewrite itself.

##### **Nimlgen** [[00:33:51](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2031)]
Yeah, I mean, I just simply can have pattern matching to just call `to_program` and basically replace things with programs.

##### **Geohot** [[00:34:02](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2042)]
Exactly. Yeah, like, we should do that. And then I still want to. Fix the.

##### **Geohot** [[00:34:08](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2048)]
I think. How is the fix of the hip compiler thing in example two hip going? Why is this still required? It should be done by the lowering pipeline.

##### **Chenyu** [[00:34:28](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2068)]
Oh. Yeah.

##### **Geohot** [[00:34:36](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2076)]
Yeah, I should look at this again.

##### **Chrism** [[00:34:38](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2078)]
But, yeah, I had last last week when I looked at it, it seemed like there was a lot of that code was sort of moving around. But I'll look at it again and see.

##### **Geohot** [[00:34:51](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2091)]
Yeah, I mean, this is a cross-collaboration issue. I think, Nimlgen, it's mostly yours making sure that, yeah, the new stuff should just call `lower_program` in the graph rewrite. And we need some way to get progress. In the context, there should be a `tqdm` that says how many compiled things there are. And then that one can call update on it and stuff.

##### **Geohot** [[00:35:14](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2114)]
Makes sense.

##### **Chenyu** [[00:35:17](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2117)]
Yeah.

##### **Geohot** [[00:35:20](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2120)]
Yes, we put a TQDM in the context for every program that's lowered. Right. Like, we need to. This should have been done a long time ago. And I blame myself for it. Like, I had this idea of like, oh, it's so nice. Look, the. Everything is lowered right on demand. But the whole thing has evolved to just not look like this. The major graph rewrite could rewrite all the syncs to programs. And that should. We just need to communicate that status a bit better. We also need to communicate the status better if it's doing Beam. And this should be enabled with debug equals one.

##### **Geohot** [[00:35:58](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2158)]
Yeah.

##### **Geohot** [[00:36:01](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2161)]
I think it'll be great. Like, debug equals one will just say. OK. Need to compile 67 kernels. Great. OK. 0 to 67, 1 to 67. Compiling includes the Beam search. Done. You have the Beam in the graph working?

##### **Nimlgen** [[00:36:16](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2176)]
Yeah. So actually, that's the only problem is with no locals because, yeah, they are not in the graph right now.

##### **Chenyu** [[00:36:27](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2187)]
And I know if we want to put them.

##### **Geohot** [[00:36:31](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2191)]
Problem is with what?

##### **Qazalin** [[00:36:33](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2193)]
The graph.

##### **Chenyu** [[00:36:34](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2194)]
No locals. Oh. Yeah, it could be kind of like Beam, I think. Yeah. What is no locals really? I don't know.

##### **Geohot** [[00:37:02](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2222)]
I don't know. I don't know. I don't know. I just wish it doesn't regress performance if we delete the locals.

##### **Chenyu** [[00:37:09](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2229)]
Yes. I think that's it, too.

##### **Qazalin** [[00:37:12](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2232)]
Yeah. I think it regresses performance a lot.

##### **Geohot** [[00:37:16](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2236)]
I mean, I hate that there isn't even an exact answer, right?

##### **Geohot** [[00:37:21](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2241)]
Like, maybe we just need a better way to express the whole thing. The only reason no locals really needs to exist is not because of the search. Like, the search needs to be deleted. That search is ridiculous and needs to be deleted. The only reason no locals really exists is because you can have fractional things, right? Like I can have `g = 63` while `l = 16`, and it'll just know automatically not to run that last one. So I don't know. If you want to, is it easy to hack in, just like Beam?

##### **Chenyu** [[00:37:52](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2272)]
I'll take a look, yeah.

##### **Geohot** [[00:37:55](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2275)]
But I think this is great. I really like the direction things are going here. And yeah, now with the deletion of, I think it's going to be a little bit more So I see this add beam thing.

##### **Geohot** [[00:38:06](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2286)]
Where does the beam search actually happen? How come I don't see that in this?

##### **Nimlgen** [[00:38:15](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2295)]
So it happens at the same place, like get programming down to the rewrites.

##### **Chenyu** [[00:38:40](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2320)]
So I think it's going to be a little bit more Yeah, I see. OK.

##### **Geohot** [[00:38:42](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2322)]
Yeah, I think we just need to move all of that to the graph rewrite. It's a precompile everything.

##### **Chenyu** [[00:38:51](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2331)]
Yeah, that'll be.

##### **Qazalin** [[00:38:53](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2333)]
Yeah.

##### **Nimlgen** [[00:39:04](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2344)]
So actually, the status is actually, the run linear is now used to execute both in the schedule and JIT. And I still need to refactor graphs because they still use exec items. And after that, we can delete it. So they just use exec items to build graphs right now.

##### **Qazalin** [[00:39:26](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2366)]
Yeah.

##### **Geohot** [[00:39:30](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2370)]
The deletion of exec items is great. And I think, yeah, combined with this refactor, it just becomes very clear what the difference is between the whole lowering pipeline is just one lowering pipeline. It's not. There's no such thing as compiling and rendering and all of these things. OK, cool.

##### **Geohot** [[00:39:54](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2394)]
We turn your tensor graph into a large binary blob that works on GPUs.

##### **Chenyu** [[00:40:03](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2403)]
Yeah.

##### **Nimlgen** [[00:40:05](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2405)]
Yeah, I haven't really looked into the CI issue with framework machine. I'll do this this week.

##### **Geohot** [[00:40:22](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2422)]
Right. Sounds good. Next up is viz.

##### **Chenyu** [[00:40:36](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2436)]
Just merged the CLI.

##### **Qazalin** [[00:40:38](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2438)]
You can try `python -m extra.viz.cli`.

##### **Chenyu** [[00:40:45](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2445)]
If you add a debug, it will reconstruct the complete debug output.

##### **Geohot** [[00:40:53](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2453)]
It's, oh, I see. You just literally just merged that.

##### **Chenyu** [[00:40:57](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2457)]
Yeah, just merged it.

##### **Geohot** [[00:41:00](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2460)]
OK. So select a source.

##### **Qazalin** [[00:41:06](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2466)]
Any dash S-O.

##### **Geohot** [[00:41:08](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2468)]
I see. OK, so now it kind of like it shows the debug equals two stuff. OK, I kind of like that.

##### **Chenyu** [[00:41:27](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2487)]
`--no-color`, I would say.

##### **Geohot** [[00:41:33](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2493)]
Yeah, so that shows me those things. OK, now I can select an item, which I assume is just the name. No, that doesn't work.

##### **Geohot** [[00:41:43](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2503)]
So this just violated my expectations.

##### **Geohot** [[00:41:49](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2509)]
OK, so I'm going to go back to the library.

##### **Geohot** [[00:42:02](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2522)]
And I'm going to use that. How do I use that? Dash I?

##### **Geohot** [[00:42:04](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2524)]
I mean, the expectation is that you grab in the profiler. What? How do I print the source?

##### **Geohot** [[00:42:21](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2541)]
How do I print debug equals four?

##### **Geohot** [[00:42:22](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2542)]
Can you get the source?

##### **Geohot** [[00:42:23](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2543)]
Yeah.

##### **Geohot** [[00:42:24](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2544)]
Oh, you just put the equals four.

##### **Qazalin** [[00:42:26](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2546)]
Oh, OK.

##### **Geohot** [[00:42:26](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2546)]
Debug equals four. I see. What if that's the source? Put debug equals one. OK, it still prints things.

##### **Qazalin** [[00:42:35](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2555)]
Yeah, so the default is `DEBUG=2` style. And then you can go up to `DEBUG=4`.

##### **Geohot** [[00:42:42](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2562)]
Why would I put debug equals four?

##### **Geohot** [[00:42:44](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2564)]
Did it load all of these libraries? So you want like dash dash debug or?

##### **Geohot** [[00:42:56](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2576)]
No, I don't know. I just don't know why it loaded. Debug equals is fine. I just don't know why it loaded all the libraries.

##### **Qazalin** [[00:43:03](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2583)]
I think because of the import, like pickling.

##### **Geohot** [[00:43:10](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2590)]
So maybe the same will be bug in pickle.

##### **Geohot** [[00:43:13](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2593)]
Yeah. Did you mean split range? That's pretty nice.

##### **Qazalin** [[00:43:19](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2599)]
Oh, yeah, yeah. There's a did you mean because LLM's often sometimes.

##### **Geohot** [[00:43:26](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2606)]
OK.

##### **Qazalin** [[00:43:26](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2606)]
OK.

##### **Geohot** [[00:43:28](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2608)]
OK. OK. OK. OK. So how much stuff is replicated here? How much code is shared? How much code is replicated?

##### **Qazalin** [[00:43:39](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2619)]
`viz` CLI shares everything with the server. The only thing it adds is printing. And the viz server just encodes the stuff, so there's a decoder on the CLI side.

##### **Geohot** [[00:44:05](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2645)]
Wait, what?

##### **Geohot** [[00:44:06](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2646)]
She's like Mamborom.

##### **Qazalin** [[00:44:07](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2647)]
Yeah.

##### **Geohot** [[00:44:08](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2648)]
That looks pretty nice. So I see a very fundamental difference between this like. Like I almost don't expect this like two-layer thing, where there's like the profile and the rewrite.

##### **Geohot** [[00:44:26](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2666)]
Well, they're fundamentally different. はい. Or maybe it's just get program and you put the rewrite and debug those four of get program. Maybe. How come those things don't line up? Delay is too large.

##### **Geohot** [[00:45:00](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2700)]
Oh, oh, so delay is I say, delay is how long it takes to get the packet.

##### **Qazalin** [[00:45:10](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2710)]
Delays the time between issuing it actually makes that thing.

##### **Geohot** [[00:45:17](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2717)]
All right, cool. How good are LLMs at using this?

##### **Qazalin** [[00:45:21](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2721)]
Yeah. LLMs are very good at using the profiler now since Friday because they added JSON support. They just put the file in JSON and then you just grep on the JSON.

##### **Geohot** [[00:45:35](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2735)]
What's JSON L?

##### **Qazalin** [[00:45:38](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2738)]
JSONL just means line, but you can put JSON and it will work. Like this parses nicely this way. Both JSON and JSONL will produce this.

##### **Geohot** [[00:45:48](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2748)]
Yeah, I wouldn't even call it JSON L. I would just call it JSON. So I'm trying to use JSON and I don't know how. I put JSON and it still gives me a list here.

##### **Geohot** [[00:45:59](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2759)]
Not in the SQTT?

##### **Geohot** [[00:46:02](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2762)]
Not SQTT.

##### **Geohot** [[00:46:04](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2764)]
I don't know. Oh, I'm supposed to know that's related to SQTT?

##### **Qazalin** [[00:46:08](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2768)]
No, it will always put JSON, but not in the list. It's like `-s all` or something. I should make `-s all` default. But I don't know. I'm just trying to figure out what the SQTT will get.

##### **Geohot** [[00:46:26](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2786)]
Yeah, OK. I see. It definitely shouldn't be JSON L. I have no idea what that means. JSON will work too. Yeah.

##### **Geohot** [[00:46:36](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2796)]
I understand that it works, but that shouldn't be what the help thing is, right? Like I'm confused at that, looking at that as a human. And LLM will be confused as well. OK. Profile path, rewrite path. So I actually think that those shouldn't be separate options. I think that that should just be like dash P and then the path, right?

##### **Geohot** [[00:47:06](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2826)]
Like dash P and then have an optional path?

##### **Geohot** [[00:47:10](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2830)]
Mm-hmm.

##### **Geohot** [[00:47:14](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2834)]
Oh, yeah.

##### **Geohot** [[00:47:14](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2834)]
I mean, fundamentally, this comes down to like I'm just trying to behave like an LLM here as best as I can. I'm just like trying things. Yeah. I mean, fundamentally, this comes down to like how good LLMs can be at using this. I kind of want to replicate that.

##### **Geohot** [[00:47:30](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2850)]
Do we have M3 Maxes? I do.

##### **Geohot** [[00:47:37](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2857)]
Do you have an M3 Max?

##### **Qazalin** [[00:47:39](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2859)]
Yeah.

##### **Geohot** [[00:47:40](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2860)]
Great. Can we replicate that Kimi thing? It doesn't matter. It's not an M3 Max. It can be on anything.

##### **Geohot** [[00:47:50](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2870)]
But I want to basically replicate like can we keep an agent running for 12 hours where we can also use, I have Kimi 2.6 running on AMD too. We could use that. We could use that. Just use a normal `7900 XTX`. But what I want to replicate is being able to have an agent run for 12 hours and make continued progress. Like I think that's your project. I think that is the culmination of this viz project.

##### **Geohot** [[00:48:23](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2903)]
Replicating that Kimi graph. Make sense? Kimi graph?

##### **Geohot** [[00:48:37](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2917)]
Oh, I posted it. But yeah. Yeah, it runs for a while. Okay.

##### **Geohot** [[00:48:42](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2922)]
Yeah. So they had something run for 12 hours that just, you know, it used Zig. But it should be able to do this in tinygrad too. Like it should be easy enough for it to create custom kernels in tinygrad for it to control

##### **Geohot** [[00:49:00](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2940)]
the fusion, all that stuff.

##### **Geohot** [[00:49:05](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2945)]
Do you control the fusions?

##### **Geohot** [[00:49:09](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2949)]
Yeah. We shouldn't be using M3 Max. We should be using `7900 XTX` where we can do this. How do you control the fusion?

##### **Geohot** [[00:49:16](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2956)]
That's a good question.

##### **Geohot** [[00:49:21](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2961)]
You write the, you write the stuff in Uops.

##### **Geohot** [[00:49:24](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2964)]
Yeah.

##### **Qazalin** [[00:49:27](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2967)]
Yeah. Do you actually think they're capable of it? Because every time I like, I've been trying to get it to get `llm.py`, sorry, LLM app, be faster. It got it to like 111 tokens per second, with like adding contiguous and stuff.

##### **Geohot** [[00:49:52](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2992)]
Yeah. I mean, so there's a few like things here, right?

##### **Geohot** [[00:49:55](https://www.youtube.com/watch?v=12UzE2hXuGE&t=2995)]
Like we have to kind of like, I think the way to do this is to do one by hand and then LLMs will be able to do the rest. So, I mean, it's kind of the thing that you've already been doing, right? The same way you do like the FP8 kernels and stuff. Like maybe you do the fusions for one of these LLMs manually. Yeah. And we need to show the LLM that you can code kernels in like multiple different ways. You can either code in, and this is like what abstractions force. You can either code in tinygrad, you can code in UOps, you can code in HIP, or you can code in assembly.

##### **Qazalin** [[00:50:34](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3034)]
Yeah. I think the place where I saw abstractions sort of break down was when I actually told it to look at LLM. It didn't comprehend the fact that tinygrad will deal with the contiguous. It felt like it had to fuse the entire dequant with the FFN.

##### **Geohot** [[00:51:01](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3061)]
Sick.

##### **Qazalin** [[00:51:02](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3062)]
And it's like, this is too hard. I have to change the G golf. Like there's all these like randomness that comes in when you actually put it in the hands of the agent. Yeah. So I think I have to do one manually, like maybe the coin one.

##### **Geohot** [[00:51:20](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3080)]
Yeah. And then like you do one manually and you use these tools. So also, Wozpar said that he wasn't using your profile. He was using his profiler because it does this classification.

##### **Geohot** [[00:51:32](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3092)]
What can we do about that? I'm hoping Jason will fix those.

##### **Geohot** [[00:51:45](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3105)]
How does Jason fix it?

##### **Qazalin** [[00:51:48](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3108)]
Because like I try to make the profile very generic. Like it will output basically, it's a basically like a debug replayer. It's not going to categorize stuff, but it will print all the markers. Like at this place, there was the marker for a train step. Then there's all these AMD devices. Then there's a tiny device. So. The agents are very good at taking that JSON and then piping it into some Python. I think I'm happy with that. Because the main thing the visprofiler is solving is stuff like relating the timestamps

##### **Geohot** [[00:52:29](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3149)]
and making sure those are right. Yeah. I think you know what your project is for the next couple weeks.

##### **Geohot** [[00:52:48](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3168)]
And it's just basically to replicate that Kimi thing. Make sure that it can use the profiler. And yeah, we shouldn't be using M3 Max. We should be using RDNA 3. And I want to go like beyond. I want to get Qwen at the memory bandwidth limit.

##### **Qazalin** [[00:53:05](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3185)]
It needs to be like a mega-kernel. I mean, like I looked at it, it needs to be like a mega-kernel, which is fine.

##### **Geohot** [[00:53:12](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3192)]
All right. Well, we shouldn't be writing those ourselves. We should be having the LLM stuff. I think Kimi can implement that stuff.

##### **Geohot** [[00:53:22](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3202)]
Writing mega-kernel?

##### **Geohot** [[00:53:24](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3204)]
Yeah.

##### **Geohot** [[00:53:25](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3205)]
Kimi can add support for that stuff. It's trying right now.

##### **Geohot** [[00:53:34](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3214)]
Oh, it got a small reward, not big rewards.

##### **Geohot** [[00:53:37](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3217)]
They want to see big progress.

##### **Qazalin** [[00:53:41](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3221)]
With something that has already existed.

##### **Geohot** [[00:53:42](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3222)]
Yeah, but it also depends on what the actual progress will look like.

##### **Qazalin** [[00:53:46](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3226)]
All right.

##### **Chenyu** [[00:53:46](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3226)]
If you only have a handful of slow ones, maybe. That seems to be mapped to that actual graph. There's one very big jump in the middle, and the rest are more incremental.

##### **Geohot** [[00:54:13](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3253)]
Yeah, I mean, I don't know where we already

##### **Geohot** [[00:54:14](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3254)]
are at on that graph. But eventually, the way that I see this working is like, it's called HyperBeam. And we run HyperBeam, and HyperBeam goes in and rewrites all your code for you.

##### **Chenyu** [[00:54:31](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3271)]
OK, let's try to speed up a little bit. And next, we have the LLM app.

##### **Geohot** [[00:54:41](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3281)]
Yeah, I'm good. Yes, I moved the LLM app to the `llm` directory. Just did a bunch of refactors on it. I'm going to move dequant to LLM loaders. We'll be able to have some other loaders in there too. Look, isn't LLM an application? Shouldn't LLM be in the TinyGrad repo? And my argument is absolutely yes, because eventually, HyperBeam itself is going to use the LLM. Like, the LLM is a part of TinyGrad.

##### **Chenyu** [[00:55:20](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3320)]
Oh, it is. It's like, do we include Claude Code in our codebase?

##### **Geohot** [[00:55:26](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3326)]
Do we include which?

##### **Chenyu** [[00:55:28](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3328)]
Include Claude Code in TinyGrad?

##### **Geohot** [[00:55:32](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3332)]
Some limited version of it, I think so, yeah.

##### **Qazalin** [[00:55:35](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3335)]
OK.

##### **Geohot** [[00:55:36](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3336)]
Not cloud code, no. Obviously, we're not trying to build a user-facing thing. But what we are trying to do is make the LLM. I think this agentic thing is cute and that it can call things. But realistically, that's not what you care about. You don't want it to be able to call any bash thing on your system. Not only is that crazy and secure, you're asking, also, why is it capable of doing that? Like, eventually, this stuff will be, the loop will be clear what you can do. All the kernel optimization should be exposed as tool calls to the LLM.

##### **Geohot** [[00:56:20](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3380)]
The thing optimizes itself. Great. But you have callify on here, too. We'll do something with callify this week.

##### **Chenyu** [[00:56:36](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3396)]
Oh, I just saw you move something around, if you want to say anything before you do anything.

##### **Geohot** [[00:56:42](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3402)]
Yeah, yeah, yeah. So I split call into two things. I split call into function and call. A function returns something, and a call doesn't. That's really the only difference. But I found that they were just used completely differently in the library. And whatever that's true, you should just split into two ops. So function returns something, and a call doesn't. So function is just like a, think about it just as a straight up substitution. And call can be something like a program. A call doesn't return anything. A call has a sink. A call has side effects. A function, that's the difference, basically. A function doesn't have side effects. A call has side effects.

##### **Qazalin** [[00:57:22](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3442)]
OK.

##### **Geohot** [[00:57:27](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3447)]
Anything to say about the broadcast?

##### **Chenyu** [[00:57:29](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3449)]
I think the broadcasting is probably fine. I don't have a huge opinion on that.

##### **Geohot** [[00:57:37](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3457)]
Yeah, it's very slow going. It takes a long time. I've been spending a lot of time just drawing things on the board. But yeah, I think I know how to do it. It's not very complex. It's almost going to delete the entire expander. And then it simplifies the devectorizer. And then we have a lot of repeated UOps. `GEP` shouldn't exist. `GEP` should just be `index`. And those other even more ridiculous ones, like pointer cat and broadcast. I think we have broadcast. It's just moving up. We can add cat.

##### **Chenyu** [[00:58:15](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3495)]
One small thing to note before you add any new uop method. We now need to be careful that the name doesn't collide with some actual tensor function that we want to use. So for example, invalid. I need to change one of it, something like that.

##### **Geohot** [[00:58:38](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3518)]
I see, yeah. Is there a way to have a linter fail on this?

##### **Chenyu** [[00:58:46](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3526)]
No, no. I mean, it would be obvious once the mixing is done, right? Because every function they share will be shared. It's just now in the middle of the migration, you will see it collides with existing stuff.

##### **Qazalin** [[00:58:58](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3538)]
Got it. Yeah.

##### **Chenyu** [[00:59:01](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3541)]
So I'm going to try to do it again.

##### **Geohot** [[00:59:02](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3542)]
I'll be fast.

##### **Chenyu** [[00:59:04](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3544)]
So tensor UOp mixing. Right now, the only bottleneck is the `full` one. And because of the unique const, you can see my latest thing that I will sync tomorrow. I might just merge that. I tried the copy-on-write and different versions of injecting the unique and all failed for different reasons. Sorry. Yeah. And I think this is probably good enough.

##### **Geohot** [[00:59:32](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3572)]
Yeah.

##### **Chenyu** [[00:59:34](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3574)]
And with that move, that just unlocks `arange` and pretty much everything that builds on top of `arange`. And I think at the end of that, that should be it. For now, I still keep some of the Winograd stuff still in tensor. I keep all the image stuff still in tensor. We can decide what we want to do. I think Winograd, we eventually want it to be a rewrite somewhere in `rangeify`. So I don't see moving that into mixin. Image, I don't know. I don't have a huge preference.

##### **Geohot** [[01:00:16](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3616)]
Why are cast and bitcast still in tensor?

##### **Chenyu** [[01:00:23](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3623)]
Because they mean slightly different things. Mm. Mm. This is the same thing for the div and mod. I think I will leave at the end because these are kind of, we will find a way to clean these up, not like actually we need to move it.

##### **Geohot** [[01:00:42](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3642)]
Yeah. I want these to sort of be unified.

##### **Chenyu** [[01:00:47](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3647)]
Yeah. So I think the way to do that is this will be unified. I also want to do that. It's just there's not a clean way to do it yet.

##### **Qazalin** [[01:00:58](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3658)]
Yeah.

##### **Geohot** [[01:01:00](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3660)]
Yeah.

##### **Chenyu** [[01:01:01](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3661)]
Yeah. So div and mod is slightly more annoying because in tensor level, there is no mod. Mod is only introduced later. But in the UOp, we sometimes call the mod directly. And sometimes we want the other form. So these are minor annoyances. We have several very basic fundamental blocks that in UOp are really overloaded. And in different states, we want them to be different things.

##### **Geohot** [[01:01:33](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3693)]
What do you mean? There's definitely a mod in tensor.

##### **Geohot** [[01:01:39](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3699)]
I wrote a quadratic sieve with this last week. It was a mod.

##### **Chenyu** [[01:01:43](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3703)]
Yeah. But that mod is using div. It's not op star mod.

##### **Geohot** [[01:01:50](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3710)]
Oh, I didn't know that.

##### **Chenyu** [[01:01:52](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3712)]
Interesting. Yeah. It's an `A - A div B multiplied by B`. Because in UOp, the mod and div is C div and C mod. But in tensor, it's not.

##### **Geohot** [[01:02:05](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3725)]
Yeah.

##### **Chenyu** [[01:02:08](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3728)]
So there's that. There's two other ones that is slightly annoying. So anyway, these fundamental blocks, I think it's fine to leave at the end of this and move the other thing that has real function.

##### **Qazalin** [[01:02:23](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3743)]
Yeah.

##### **Chenyu** [[01:02:24](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3744)]
So that's pretty much it. I will think about your other performance. I think it's a very good proposal, variable after maybe end, maybe next week. We can discuss about that.

##### **Geohot** [[01:02:34](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3754)]
Yeah. Yeah. It's very confusing to use. I think it should kind of just be tensor. And we should work on scatter and gather being good.

##### **Geohot** [[01:02:44](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3764)]
Yeah, sure.

##### **Geohot** [[01:02:46](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3766)]
You should be able to scatter based on a math thing with A range, right?

##### **Chenyu** [[01:02:53](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3773)]
That is only good if it's A range. That's the annoying part, for sure. Let's discuss this next time. I also think about this a lot.

##### **Geohot** [[01:03:02](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3782)]
Sure. I mean, you should be able to multiply by 2. Or you should be able to scatter on an index tensor times 2 or something. We shouldn't have something special called variable that you can scatter based on. Or maybe you can already do that. I don't know. I wrote the quadratic CF stuff. And wow, tinygrad is fast. And I don't think any other library can do this.

##### **Geohot** [[01:03:21](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3801)]
And it's fundamentally because we can fuse math and a reduce.

##### **Geohot** [[01:03:31](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3811)]
Great. Sounds good.

##### **Chenyu** [[01:03:33](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3813)]
OK, we go a little bit out of time. But I want to quickly discuss, how do we make Comma happy?

##### **Geohot** [[01:03:42](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3822)]
I see torpboy in here.

##### **Chenyu** [[01:03:45](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3825)]
Yeah. He also just post his thought on stuff, right?

##### **Geohot** [[01:03:50](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3830)]
Yeah. Yeah. We got to address that. I mean, we fixed one of the issues, apparently. I think we are fixing the issues.

##### **Chrism** [[01:04:00](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3840)]
The other thing that I think is probably an issue for Comma is the fact that we're downloading AMD firmware. We'll probably need to figure out a better solution for that.

##### **Geohot** [[01:04:12](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3852)]
Oh. Yeah, I'm supportive. Do you want to take that project? Yeah. After the dev and the abstractions clean up? Yeah, I think we just need to figure out how we want to auto-gen or something. Yeah. We shouldn't be. The internet should not be a requirement.

##### **Chrism** [[01:04:30](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3870)]
Yeah, for sure. For sure.

##### **Geohot** [[01:04:31](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3871)]
Yeah. We got to auto-gen without these files being massive.

##### **Chrism** [[01:04:35](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3875)]
Yeah. The headers, for sure. I don't know what I think about the binaries. But yeah.

##### **Wozeparrot** [[01:04:40](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3880)]
Yeah, it's the binary firmware. That's the annoying one.

##### **Geohot** [[01:04:43](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3883)]
Oh. Yeah, I don't know. I don't have an obvious solution for that.

##### **Chenyu** [[01:04:52](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3892)]
I think generally, just something good is, they say they waste hours to do something, right? And it's not clear if it's because TinyGrad is still alpha-ish, brittle, and things are changing. If that's the case, maybe it's like, OK, we will fix your issue. But just generally, given that other external users who try to use TinyGrad would probably just get a much worse experience, we will use this as like, see where we can improve. Maybe it's just having better error messages. Maybe it's just, well, something.

##### **Geohot** [[01:05:36](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3936)]
Yeah, I mean, as we get closer to implementing the spec, I think like, you know, mixins.

##### **Geohot** [[01:05:45](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3945)]
Oh, you saw how I eventually think that mixins are going to create functions, right?

##### **Chenyu** [[01:05:49](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3949)]
Yeah, yeah. It's like, that's kind of how I think. It's like how I write this. So tensor will be just a thing like an entry point.

##### **Geohot** [[01:05:59](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3959)]
Yeah, and then it'll unpack the UOp to the function, and then that's metadata, basically. I think when we have all this stuff, like, this is how we can really improve our error messages. 1.0 is in sight.

##### **Geohot** [[01:06:13](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3973)]
It is still years away, but probably not 3 years away.

##### **Chenyu** [[01:06:23](https://www.youtube.com/watch?v=12UzE2hXuGE&t=3983)]
Okay. Anyway, I think we have enough resources to help out with the Comma issue. But on a more meta level, just take this as an opportunity to, I think one is to see how Claude can help issues with tinygrad dev faster. I think Comma is already using that. Then second is just find a better way to not waste their time and not waste our time. Find a balance between this.

##### **Qazalin** [[01:06:50](https://www.youtube.com/watch?v=12UzE2hXuGE&t=4010)]
Okay. Thank you.

##### **Chenyu** [[01:06:53](https://www.youtube.com/watch?v=12UzE2hXuGE&t=4013)]
It's just sad to see that your user says they waste tons of time. So let's try to do that.

##### **Geohot** [[01:07:01](https://www.youtube.com/watch?v=12UzE2hXuGE&t=4021)]
Yeah. At least hopefully it wastes Comma's time.

##### **Wozeparrot** [[01:07:06](https://www.youtube.com/watch?v=12UzE2hXuGE&t=4026)]
Do you want to merge my USB tuning changes?

##### **Geohot** [[01:07:11](https://www.youtube.com/watch?v=12UzE2hXuGE&t=4031)]
Oh, yeah. You don't have access to repo? No, I don't. I'll just add you.

##### **Qazalin** [[01:07:17](https://www.youtube.com/watch?v=12UzE2hXuGE&t=4037)]
Okay. Okay. Great.

##### **Geohot** [[01:07:26](https://www.youtube.com/watch?v=12UzE2hXuGE&t=4046)]
I think that's it for today.

##### **Wozeparrot** [[01:07:28](https://www.youtube.com/watch?v=12UzE2hXuGE&t=4048)]
And for everyone here next week.

##### **Chenyu** [[01:07:31](https://www.youtube.com/watch?v=12UzE2hXuGE&t=4051)]
I will post the, since it's a new day, I will post maybe the day before or something like that. The day before. It also happened to be a Monday. So you will see.

##### **Qazalin** [[01:07:44](https://www.youtube.com/watch?v=12UzE2hXuGE&t=4064)]
Okay.

##### **Chenyu** [[01:07:45](https://www.youtube.com/watch?v=12UzE2hXuGE&t=4065)]
I think that's it for this meeting. Thank you, everyone. Until next week. Bye bye.

##### **Geohot** [[01:07:50](https://www.youtube.com/watch?v=12UzE2hXuGE&t=4070)]
Thank you. Bye.

##### **Qazalin** [[01:07:51](https://www.youtube.com/watch?v=12UzE2hXuGE&t=4071)]
Bye.
