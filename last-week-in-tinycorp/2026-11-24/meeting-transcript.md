# 2026-11-24 Meeting

### Meeting Agenda

**Time:** new meeting #47, 11/24 12pm Hong Kong time
- company update, release?
- llm token service
- CI machines
- export compile run
- speedup cleanup fixup
- assembly ASM NATIVE CALL
- hcq2 driver
- comma, bounty, other issues


### Audio

[Youtube Link](https://www.youtube.com/watch?v=2hV3Y0TMPd0)

### Highlights

- **[Company Update](#geohot-000006)**: MI300 machines are for sale. The LLM token service is launching soon with free Qwen Flash and GLM Flash tokens. The team is moving from BEAM toward "Slop," which uses an LLM to optimize your kernels.
- **[Tinygrad Direction](#geohot-000256)**: The goal is to replicate Neon's kernel-writing results with open models. Tinygrad's value is letting you ship and maintain those kernels. The new slop kernels repo stays within the tinygrad language, and agents change the kernels rather than the language.
- **[Release](#chenyu-000437)**: Chenyu wants a release before the next big changes (compile, export, device). The last release was about three months ago and MLPerf is now done.
- **[Slop Kernels Packaging](#geohot-000745)**: Following Chrism's `tinygrad[slop]` extras idea, slop kernels will be a separate package that depends on tinygrad, not a submodule or part of the mega-repo.
- **[LLM Token Service](#wozeparrot-000832)**: The service is launching now. The public invite link gives an account with one credit, and more credits can be requested in the channel. Employees must not use that link, since Wozeparrot would have to change their accounts.
- **[CI Machines](#geohot-001754)**: To deal with the Chestnut USB instability, Geohot suggests a CI step that resets the device and retries up to 10 times. He also thinks the firmware can be fixed with LLM help. Chrism agrees to add the retry.
- **[Gitea and Scrapers](#chrism-001827)**: Gitea is now exposed with direct SSH and own SSL termination, so Cloudflare bot blocking is gone. Scrapers must now be blocked in Caddy and EdgeRouter. The compare API is especially expensive.
- **[Private Stats](#geohot-002427)**: Geohot is fine with making more infrastructure private and doesn't want a battle against scrapers. The team agrees to make stats non-public by turning off Grafana anonymous access, which allows IP-level logging.
- **[Tinygrad Phases](#geohot-002853)**: Tinygrad breaks into five phases: export, compile, load, link, and run. As much as possible moves into compile, which is pure, device-free, and cacheable. The JIT becomes just link and run.
- **[Speed and Reliability Push](#geohot-003316)**: Geohot will be out for the next two meetings on his yearly bike trip. He wants everyone focused on fast, reliable CI machines and a fast tinygrad: "speed is the moat."
- **[CI Speedups](#chenyu-003631)**: Chenyu reviewed 100 days of CI runs and removed tests that never fail or catch regressions, cutting about two minutes of runtime.
- **[Rangeify Rewrite](#chenyu-004112)**: A minus-200-line change to the rangeify algorithm looks like a sound direction, though it is currently broken. Chenyu will add tests and review it, and Geohot is generally supportive.
- **[NATIVE Instruction Selection](#qazalin-004455)**: NATIVE expresses explicit backend-specific instruction selection, with source zero holding the UOp implementation. This lets backend kernels be verified on the emulator without opening the device.
- **[HCQ2 Driver](#nimlgen-005114)**: Nimlgen is loading HCQ2 programs at runtime on the Chestnut project, which has only about 52 KB of free SRAM. The AMD driver has been rewritten with UOps, but fitting it into that space is hard.

### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=0)]
Welcome everyone, we'll start with company update.

##### **Geohot** [[00:00:06](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=6)]
We have MI300 machines for sale, buy some MI300 machines. That's pretty much it. Oh yeah, and we also got hopefully our LLM token service launching very soon. Which is going to give you some free Qwen Flash tokens and some free GLM Flash tokens. So we're going to be moving away from things like BEAM and tinygrad, and we're going to be moving towards Slop. So Slop is the replacement for BEAM eventually. SLOP will basically connect to an LLM and use that LLM to optimize your kernels.

##### **Geohot** [[00:00:53](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=53)]
It's kind of nice that we also have a convenient token service that will perhaps be built into this. Of course, when you get free tokens, we might be logging. We're not logging anything right now, but no guarantees in the future. It'd be kind of nice: you get free tokens, use those tokens to optimize kernels, and then [unclear].

##### **Geohot** [[00:01:22](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=82)]
So, yeah. But it's really important that we build really good infrastructure for serving tokens, for CI machines, for GPUs and CI. Having reliable infrastructure that agents can quickly use is important. The Incus stuff is amazing. You no longer have to think about whether the GPU in your computer is in use. Just grab it and use it. Neon is writing YAML files that just submit jobs to CI.

##### **Geohot** [[00:02:03](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=123)]
And yeah, I mean, this is how things are repeatable, reliable, scalable, and so forth. That is what the tinygrad project is becoming. We have to think about how to make tinygrad a very minimal thing that just cleanly launches the kernels. The decisions, all of these heuristics that made old compilers so complex, I've always said were going to be search. I just didn't realize how completely unstructured this search was going to be. If you haven't tried it, try Neon. Neon is not nerfed. Fable was nerfed pretty badly on purpose by Anthropic to prevent you from having fast kernels. But try Neon. It's not nerfed, and it makes fast kernels.

##### **Geohot** [[00:02:56](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=176)]
But yeah, we should be able to replicate basically what Neon's doing with open models. And then tinygrad will be self-optimized. But the key thing that tinygrad is going to give you is the ability to actually ship that. Right? If you have Neon just write you C++, you know, a whole lot of C++ stuff, yeah, I mean, that's fun. And it's fast. But how do you ship and maintain that? Whereas tinygrad will keep this confined. The new slop kernels repo is just within the tinygrad language. You know, think about how all these math proofs are happening in Lean, but the agents aren't changing Lean. The agents are changing proofs. And that's how we think about it.

##### **Chenyu** [[00:03:51](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=231)]
Sounds good. Can we do a release before all of that?

##### **Geohot** [[00:04:00](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=240)]
Yeah, we should do a release. I mean, the diff that uses slop kernels is a massive red diff.

##### **Geohot** [[00:04:18](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=258)]
Do we also release that?

##### **Chrism** [[00:04:22](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=262)]
Slop kernels? Yeah.

##### **Geohot** [[00:04:28](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=268)]
Yeah, I mean, I don't think that that's included in the, I don't know.

##### **Chenyu** [[00:04:34](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=274)]
Okay.

##### **Geohot** [[00:04:35](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=275)]
We'll have to see how to do it.

##### **Chenyu** [[00:04:37](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=277)]
Our last release was like three months ago, and now MLPerf is done. I figure it's a good time before we do another very big rewrite of everything.

##### **Geohot** [[00:04:48](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=288)]
I mean, I don't think this is a big rewrite of everything. It's basically just moving all the kernels from tinygrad.

##### **Chenyu** [[00:04:53](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=293)]
I mean, the upcoming compile, export, device changes, whatever.

##### **Geohot** [[00:05:04](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=304)]
Yeah. I mean, maybe we do want to include slop kernels in the releases. We can figure out how to like package this properly.

##### **Chenyu** [[00:05:11](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=311)]
Yeah.

##### **Geohot** [[00:05:14](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=314)]
What I want to do is start pointing LLMs at all the slop kernels and just say, "Make these faster." I'll point them at [unclear], I'll point them at everything and just steal every one of their tricks in the kernels. We'll end up with these insanely fast kernels. I think Neon can also write assembly and use these.

##### **Chrism** [[00:05:36](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=336)]
So, kernels are about to get very fast.

##### **Geohot** [[00:05:40](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=340)]
And then we just need to improve and really make beautiful the core tinygrad so that all you're left with is kernel overhead. That's improving the HCQ stuff so that there's less time between launches. That's improving the rangeify stuff so that contiguous is everywhere. It makes sense.

##### **Chenyu** [[00:06:07](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=367)]
Great. Anything else for company update?

##### **Geohot** [[00:06:12](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=372)]
No. But yeah, on the release, yeah, we should figure out how to package slop kernels with that. I don't know.

##### **Chenyu** [[00:06:19](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=379)]
Like add a submodule or something? I don't know. Wozeparrot can figure this out?

##### **Wozeparrot** [[00:06:27](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=387)]
Yeah, I'll look into it. I don't like Git submodules. I don't think most people like Git submodules.

##### **Geohot** [[00:06:32](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=392)]
Yeah. I don't know. I don't think it should be a submodule. I think that we could probably just, you could just clone it and we'll just clone it and put it in the release. I might want to put it inside the tinygrad folder. So it might be like tinygrad, docs, slop kernels.

##### **Chrism** [[00:06:52](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=412)]
The extra is actually fine.

##### **Geohot** [[00:06:59](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=419)]
Wait, what do you mean?

##### **Chenyu** [[00:07:03](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=423)]
We used to have a bunch of random files in HTML. And we never packaged those.

##### **Geohot** [[00:07:09](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=429)]
Yeah, no, I know. It's annoying. So maybe I do want to put it in like tinygrad slash slop kernels. And yeah.

##### **Chrism** [[00:07:19](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=439)]
You could make it like one of the extra dependencies things. So like you do like `pip install tinygrad[slop]`.

##### **Geohot** [[00:07:31](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=451)]
And make slop kernels its own package?

##### **Chrism** [[00:07:36](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=456)]
That's the idea. Yeah.

##### **Wozeparrot** [[00:07:39](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=459)]
Okay. Okay, fine. That's the nicest way to do it. Yeah, I think that's the nicest way to do it.

##### **Geohot** [[00:07:45](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=465)]
Okay. I'll make it a package. It'll be a separate package. And it has a dependency on tinygrad.

##### **Chrism** [[00:07:55](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=475)]
Which, yeah, I mean, we shouldn't be shoving everything into the MegaRepo.

##### **Geohot** [[00:08:03](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=483)]
And this has a clear distinction. The code in tinygrad needs to be very, very high quality and small. The code in slop kernels needs to be fast and well tested.

##### **Chenyu** [[00:08:19](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=499)]
Okay, that sounds good. Let's move on to the LLM token service.

##### **Wozeparrot** [[00:08:26](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=506)]
I guess we're launching now.

##### **Chenyu** [[00:08:30](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=510)]
Is it launched?

##### **Wozeparrot** [[00:08:32](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=512)]
Are we good? There's the invite. There's the invite link if people want to sign up for it. They'll give you an account with one credit. You can always request more credits in the channel. I think we're doing that for now. If you're an employee, do not sign up with that link or else I have to change your account.

##### **Chenyu** [[00:08:52](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=532)]
Wait, wait, what? I almost clicked it.

##### **Geohot** [[00:08:57](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=537)]
I mean, every employee should sign up with their, we have an employee link too. Yes, there's an employee link

##### **Wozeparrot** [[00:09:02](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=542)]
that will give you an account with unlimited usage. Okay.

##### **Geohot** [[00:09:06](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=546)]
And all the good models

##### **Wozeparrot** [[00:09:07](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=547)]
too. Yes.

##### **Chenyu** [[00:09:09](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=549)]
Then who is going to test this link?

##### **Wozeparrot** [[00:09:14](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=554)]
I already tested the link and it worked.

##### **Geohot** [[00:09:17](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=557)]
Okay. Okay, so in tokens by account, I see a bunch of accounts that don't have a name.

##### **Wozeparrot** [[00:09:26](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=566)]
So some of those are legacy accounts or just like my testing accounts that are just there?

##### **Geohot** [[00:09:36](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=576)]
I see. Yeah.

##### **Wozeparrot** [[00:09:39](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=579)]
It goes back seven days.

##### **Geohot** [[00:09:43](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=583)]
Got it. And we should probably sunset the old hardcoded keys.

##### **Wozeparrot** [[00:09:50](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=590)]
Yeah. The other thing is just comma needs to switch over too. I don't know how many people, there's been usage on the comma key.

##### **Geohot** [[00:10:01](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=601)]
Yeah. Yeah,

##### **Chrism** [[00:10:02](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=602)]
they're in the process of moving their Slack bot over to a... Yeah. To that.

##### **Geohot** [[00:10:11](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=611)]
Yeah. If you're an employee or you're an employee with comma, you get unlimited. Oh, I see people coming in. Also, yeah, make sure to check out. So if you sign up for that thing, you can use gpt.party. Yeah.

##### **Geohot** [[00:10:39](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=639)]
Yeah, but we should move comma to whoever wants to sign up with their GitHub. I don't know what we do with like their bot. If you're an employee, yeah, you get unlimited Kimi tokens. Everyone else gets flash tokens. Do we have an easy way to like, can I like make an account, can I like give someone Kimi tokens?

##### **Wozeparrot** [[00:11:04](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=664)]
Give someone Kimi tokens. Yeah.

##### **Geohot** [[00:11:08](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=668)]
Yeah, Is there an admin panel?

##### **Wozeparrot** [[00:11:10](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=670)]
There's no admin panel. There's an API and a command line tool.

##### **Geohot** [[00:11:15](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=675)]
Probably fine. If someone has signed up with GitHub with that link, is there a way for me to give them credits and give them Kimi access? It's okay if it's command line.

##### **Wozeparrot** [[00:11:35](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=695)]
There's a way to give them credits and you can move them to an entitlement that has Kimi access.

##### **Geohot** [[00:11:43](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=703)]
I see. And then is, does Kimi have credits too?

##### **Wozeparrot** [[00:11:51](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=711)]
Kimi is not priced right now, because I don't know what to price it at.

##### **Geohot** [[00:11:55](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=715)]
We probably just want to price everything. Employee accounts are allowed to have negative balances.

##### **Chrism** [[00:12:09](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=729)]
Yeah, accounts will go to a negative balance.

##### **Geohot** [[00:12:15](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=735)]
Well, our accounts can go negative. Public accounts can't.

##### **Wozeparrot** [[00:12:22](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=742)]
They can go negative balance if you're in the middle of the generation and you run out of credits. I looked at most of the routers and none of them have a good way around this. It's all soft limiting.

##### **Geohot** [[00:12:34](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=754)]
Yeah, yeah, yeah. The middle of the, that's all fine. But I'm saying like, employee accounts can go massively negative.

##### **Wozeparrot** [[00:12:42](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=762)]
Employee accounts just charge zero for everything.

##### **Geohot** [[00:12:49](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=769)]
Okay. Yeah, maybe we should always charge the same, just employee accounts can go very negative.

##### **Wozeparrot** [[00:12:53](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=773)]
That's a little harder to do, but yeah. You can do that too.

##### **Geohot** [[00:12:58](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=778)]
Well, I'm just saying like, I don't think the entitlement should be like, employee or non-employee. I think that like, how much we charge versus what models we access should be like, kind of orthogonal things.

##### **Wozeparrot** [[00:13:15](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=795)]
So currently model access is tied to the entitlement. And pricing can be tied to the entitlement as well.

##### **Geohot** [[00:13:24](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=804)]
I don't know. You know the basic thing I want. Some way for a user, someone who we trust, someone who's doing work for tinygrad, we can say, "Here's your credits. Here's the models you can access." Yeah, okay. Yeah, and I'm okay if it's just basically two choices. It's kind of like, we can have the free tier models and the good tier models. Yeah, I kind of see how this would be. It's basically like temporary entitlement. Got it. I don't know. I'll just go. But cool. SnacksRaven, I see you enjoying many tokens. Are they working well?

##### **Geohot** [[00:14:21](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=861)]
Great. Feel fast? Right? And it will get even faster. We have a bunch of integration work still to do. It's a slop branch serving those tokens, but once we get all this stuff integrated and formalized, it's going to go even faster.

##### **Geohot** [[00:15:02](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=902)]
Sounds good.

##### **Chenyu** [[00:15:08](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=908)]
Anything else for the token service? We don't really advertise this service, right? It's only people who are here who know.

##### **Geohot** [[00:15:19](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=919)]
Yeah, I think that's good. Yeah. We just. It comes down to how much like we want to, we want to like stress this thing. Yeah. We want to understand as a company how to operate and. Is there any alert if the service is down?

##### **Wozeparrot** [[00:15:43](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=943)]
Not yet. I need to set that up. Yeah,

##### **Chenyu** [[00:15:46](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=946)]
I think at least some, maybe somewhere in the discord would be nice.

##### **Geohot** [[00:15:56](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=956)]
I clicked the link. It just went to my like account. Yeah. Is that okay?

##### **Wozeparrot** [[00:16:03](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=963)]
Yes. If you're already signed up, it won't change your enrollment.

##### **Geohot** [[00:16:08](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=968)]
I see I have one credit. Everyone just gets one credit on signup. Okay. Sounds good.

##### **Chenyu** [[00:16:25](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=985)]
Next is CI machines.

##### **Chrism** [[00:16:29](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=989)]
Yeah. Yeah. Yes. Yeah. So I don't know. Just generally been working on that. Things haven't been perfectly stable. I was looking into the USB stuff today. Really couldn't figure out any root causes for what's going on there. It's I don't know. I'm starting to get a little worried that these USB cards that we have are just not. Yeah. Not great. Maybe they just don't work all that great.

##### **Geohot** [[00:17:04](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1024)]
Oh, you're talking about the Chestnut instability.

##### **Chrism** [[00:17:07](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1027)]
Yeah.

##### **Geohot** [[00:17:09](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1029)]
I looked into it a bit yesterday. And there are things we can fix in the firmware.

##### **Chrism** [[00:17:15](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1035)]
Yeah.

##### **Geohot** [[00:17:17](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1037)]
Yeah. Yeah.

##### **Chrism** [[00:17:19](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1039)]
Yeah.

##### **Geohot** [[00:17:22](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1042)]
LLMs have come a long way since January when that firmware was written. They're now much better at like figuring out. There's like recovery things that the firmware has. Yeah.

##### **Chrism** [[00:17:32](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1052)]
Okay, I'll look into that. I thought, you know, comma uses the firmware so much that they probably would have run into many bugs. But probably what's happened is that we've optimized the firmware against the comma host super well, and not against our new host. So that makes sense.

##### **Geohot** [[00:17:54](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1074)]
That's exactly. I think what we should do for now is just add. Can you add just a quick retry? Like in the CI job that just resets the thing and tries it like 10 times.

##### **Chrism** [[00:18:04](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1084)]
Like tries resetting it or retries the entire job?

##### **Geohot** [[00:18:09](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1089)]
Oh, just try resetting it in the job.

##### **Chrism** [[00:18:12](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1092)]
Yeah.

##### **Geohot** [[00:18:13](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1093)]
We have the ability to do the FTDI reset, right?

##### **Chrism** [[00:18:17](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1097)]
Yes. Yes. In fact, we currently do that at the beginning.

##### **Geohot** [[00:18:20](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1100)]
Yeah. If it doesn't connect well, then.

##### **Chrism** [[00:18:27](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1107)]
Yeah. Yeah, that makes sense. Well, I'll do that. That's the easiest thing to add. The other stuff: Gitea is exposed now, so you can SSH directly to that. A consequence of that is that for HTTP we do our own SSL termination, and all that that entails. One of the important things is that previously I had Cloudflare doing some bot blocking for us, and we don't do that anymore. So we have to do that in Caddy and EdgeRouter. We need to be mindful of that. If some scraper comes online, we need to be vigilant about blocking them. There's some really expensive endpoints in the Gitea server. The compare API is really slow. I'm pretty sure it forks a git diff and just runs that, so that's really expensive.

##### **Chrism** [[00:19:44](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1184)]
The scrapers seem to love crawling through every possible permutation of pairs. That's frustrating, and we've got to keep that in mind. Yeah other than that I switched us to 10 gig internet today. So that should work. We also have Gitea backups. I tested that this morning and that like just restoring from one of them. They work. So we keep a month worth of backups that happen every night. Gitea goes offline for like 10 seconds. I set it to I think 3 a.m. Pacific time. There may be better times to set that to but that seems like pretty decent in terms of when people would not be working.

##### **Chrism** [[00:20:38](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1238)]
So you know if you find that frustrating and you're like oh why is it going down when I'm trying to work then we can move that time. But unfortunately that appears to be the only way to reliably save a backup.

##### **Chrism** [[00:20:56](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1256)]
Right. Oh yeah, the macOS stuff. I set up a couple more hosts for the Mac VMs. We can also bump that up a fair amount with the kernel extension. You just need to enable loading unsigned kexts. It's a little annoying because you have to reboot and enable the unsigned kexts manually, but you only have to do it once.

##### **Chrism** [[00:21:34](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1294)]
Yeah. That's worth doing. I should probably do that. It depends on how much we're going to be using Gitea in the future, especially to run macOS stuff.

##### **Geohot** [[00:21:49](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1309)]
Yeah. I just added a job to benchmark Qwen. Do we have 10 gig to all the AMD CI machines?

##### **Chrism** [[00:22:06](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1326)]
No. So what I'm going to do is when I switch everything over I'm just going to the thing that seemed way simpler was to just use the 100 gig cards and then just do like everything over PXE over those 100 gig cards. Those cards are nice because they. Yeah. They support like fancier PXE boot in the sense that they support iPXE out of the box. So we can just like point them at an HTTP URL rather than having to do some like crazy weird TFTP thing.

##### **Chrism** [[00:22:36](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1356)]
So I thought I would just do that and then everything would have the same network.

##### **Geohot** [[00:22:42](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1362)]
Oh. The Mellanox cards support PXE?

##### **Chrism** [[00:22:48](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1368)]
Yeah, the Mellanox cards. And I started working on that PXE-boot VM host. I've been looking at using Cloud Hypervisor, which is a project out of Alibaba. I guess they used to run VMs on their own stuff. Seems pretty good. I was able to get the full performance out of the drives in the RAID array without too much overhead. So that should be good.

##### **Wozeparrot** [[00:23:29](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1409)]
I looked yesterday and there was a bunch of scraping happening.

##### **Chrism** [[00:23:37](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1417)]
Yeah, I would believe it. I should just probably go through the logs every once in a while and make sure there's not anything. I guess maybe we can set up alerting. Gitea has like reporting for how long the page took to render. or something like this. And maybe if that average time goes way too far up, then we can set up an alert and just quickly fix that.

##### **Wozeparrot** [[00:23:58](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1438)]
We probably do want network metrics from Caddy. But we can't really have good network metrics with our current metrics stack because everything is public. There's some information we don't want to leak if we do edge metrics.

##### **Chrism** [[00:24:26](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1466)]
Yeah.

##### **Geohot** [[00:24:27](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1467)]
I'm fine with starting to make more of this stuff private. Like, I don't know. I don't want to be in a battle against scrapers.

##### **Wozeparrot** [[00:24:38](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1478)]
Yeah, because it would be really helpful if we could log IP, like accesses by IP addresses. But I don't think we want to make that information public. Yeah.

##### **Geohot** [[00:24:49](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1489)]
I don't think we do either. Yeah. I'm fine with starting to log more aggressively and making. You want to make stats not public? We can change that.

##### **Wozeparrot** [[00:25:02](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1502)]
My current plan was just to spin up another stats.

##### **Geohot** [[00:25:06](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1506)]
Nah. I think we should just make this one not public.

##### **Wozeparrot** [[00:25:09](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1509)]
OK. Yeah. We can just do that.

##### **Geohot** [[00:25:11](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1511)]
How are we going to auth it?

##### **Wozeparrot** [[00:25:16](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1516)]
It's auth. Grafana's already authed. It's currently on allow anonymous access. So if you just turn it off, you can't access it anymore without being authed.

##### **Geohot** [[00:25:25](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1525)]
Okay. And I have to have some login in the info repo or something? Yeah, that seems good. Cool. Let's go dark.

##### **Chrism** [[00:25:38](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1538)]
Yeah, so I don't want it to log me out and stuff. Yeah. And that also means InfluxDB needs to be authed, right?

##### **Wozeparrot** [[00:25:56](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1556)]
It's only exposed through Grafana.

##### **Chrism** [[00:26:00](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1560)]
Oh, great. Well, one thing that would be an upside of it being authed would be that CI could hit that. And I don't need to have like this special back door for CI to be able to reach.

##### **Wozeparrot** [[00:26:14](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1574)]
Grafana only accesses the read API.

##### **Chrism** [[00:26:22](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1582)]
Yeah, that makes sense. I can put all the gateways on the VMNet. Yeah. I think it's easier. I think that's pretty much it, unless there's other Iris or infrastructure questions. Oh, the fans are installed. I almost forgot about that. It's also much cooler in San Diego. We just did the LLM launch, but we should be good. We need to make the intake filters bigger so that they're less restrictive. Then we can feel a little better about having everything run on full blast. Right now two of the three exhaust fans are on the lower setting rather than the high-speed setting.

##### **Chrism** [[00:27:25](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1645)]
But it's certainly fine for right now. I mean, the door is closed. And you can look at the temperature numbers. And I've been working in there for whatever. Previously it was sort of unbearable, and now it feels like a normal temperature.

##### **Geohot** [[00:27:41](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1661)]
I see that we've lost fan status. I don't know.

##### **Wozeparrot** [[00:27:51](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1671)]
I turned off the environment controller because Chris asked me to.

##### **Chrism** [[00:27:56](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1676)]
I see. I didn't realize that would result in that going off. Yeah, we just wanted to, while Anton was testing that, we wanted to have them all on max so we could have a sense of. Part of the issue is that there's like, it creates a lot of negative pressure in the room because those exhaust fans are so much more powerful than the intake fans. If you turn one of the fans off right now, it'll free-spin because of the amount of air that's being pulled through.

##### **Geohot** [[00:28:38](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1718)]
OK. All good.

##### **Chenyu** [[00:28:44](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1724)]
Okay, let's move on to George's talk.

##### **Geohot** [[00:28:53](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1733)]
Yeah. So I've been breaking down kind of like the phases of tinygrad. So we can think about everything as five phases. There's export, which goes from like all of your tensor stuff, all of your buffer stuff, to UIR. We used to call this CALLify. But CALLify was way too complex. The new thing, export, just replaces all buffers and variables with EXTERNs. EXTERN means this comes from outside. Then that is a UOp or a piece of UIR that is independent. Export also returns a list of what all those EXTERNs bind to: the actual buffers and variables. The return from export, which is already available in Tensor, is a UOp with EXTERNs and a list of bindings.

##### **Geohot** [[00:29:54](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1794)]
Now the next step is compile. Compile includes scheduling, rangeify, and actual compilation. We want to move as much into compile as possible, because compile works without a device. Compile can be pure and can be cached.

##### **Geohot** [[00:30:20](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1820)]
Now the next step is load. Load loads all your programs, command buffers, everything that actually has to be loaded onto the device. Then link. Link on the device after you've loaded the command buffers. Link patches the command buffers to link to the actual buffers. That's what the JIT uses. And then run, which actually runs things. We want to put as much into compile as possible, as much HCQ and actual compilation as possible. That's how we'll get tinygrad to start up fast.

##### **Geohot** [[00:30:59](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1859)]
Been working on that. I think everybody should be thinking about this stuff. Why doesn't an LLM load in five seconds? We can cache compile entirely. I think we should just start caching it, like cache the schedule cache on disk.

##### **Chrism** [[00:31:21](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1881)]
So we need to be a little fast.

##### **Geohot** [[00:31:26](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1886)]
Yeah. And then also we can do some simplifications to the JIT based on this. The JIT should basically use the same API. This has been more and more unified over time. But of those five steps, export, compile, load, link, run, the JIT is just link and run.

##### **Geohot** [[00:31:47](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1907)]
So we can just do that. That's it for that.

##### **Chenyu** [[00:31:57](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1917)]
Will compile also take all the arch or whatever flags?

##### **Geohot** [[00:32:09](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1929)]
Any flags that can affect the compiler, a full description of the device or something. That should all be in TARGET, everything that can affect compilation. The only thing that's a little bit leaky in this API is BEAM because BEAM actually needs a device. I think maybe we just allow the device if you use BEAM. Right now there's a context var that disallows including the device, but we can just allow it.

##### **Chrism** [[00:32:42](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1962)]
What is it? [unclear]

##### **Geohot** [[00:32:47](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1967)]
So we can just do that. So we can change that. I mean, BEAM opens devices. But compilation is not actually in compile yet.

##### **Chenyu** [[00:32:58](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1978)]
Yeah. Now the current compile is kind of just one function.

##### **Geohot** [[00:33:03](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1983)]
The current compile is just scheduling. Yeah. We want to move all compilations to compile.

##### **Chrism** [[00:33:14](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1994)]
Yeah.

##### **Geohot** [[00:33:16](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=1996)]
Yeah. Without BEAM it shouldn't allow. So I'm going on my yearly bike trip, next week and the week after. I want everybody thinking about speed and reliability. How can we get these CI machines super fast, super reliable? How can we get every single part of tinygrad, export, as quick as possible? Compile is pure, so threads, all the tricks there. CI should be fast. Speed is the moat.

##### **Geohot** [[00:33:56](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2036)]
Okay. All's good.

##### **Chenyu** [[00:34:00](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2040)]
How's course going on?

##### **Geohot** [[00:34:02](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2042)]
Pretty good. For week seven, I added BARRIER. I don't know if we have BARRIER like this in tinygrad, but BARRIER should take in the ranges that it's being applied to. We have a distinction in ranges between parallel ranges and serial ranges. We've always kind of had this. LOOP is serial. The rest of them are parallel.

##### **Geohot** [[00:34:26](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2066)]
At least I think that's what it is now. Upcast is... I guess upcast, I don't know. But GLOBAL and LOCAL are parallel. And then you can do barrier. And barrier means synchronize all parallel ranges at this point. So I added the BARRIER op and a CPU threading runtime for studentgrad, which allows global ranges and barriers on those global ranges to synchronize them.

##### **Chrism** [[00:34:54](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2094)]
Yeah.

##### **Chenyu** [[00:34:55](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2095)]
We don't have barriers like that. That's most of the thing tinygrad doesn't pass for week seven.

##### **Geohot** [[00:35:02](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2102)]
I see. Also, Neon is next level. The other models can't find stuff. Neon finds more bugs.

##### **Chenyu** [[00:35:17](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2117)]
How do you use Neon?

##### **Geohot** [[00:35:20](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2120)]
Through Google. Oh, you have to use stupid Antigravity, but I just accepted it.

##### **Chenyu** [[00:35:28](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2128)]
What is that?

##### **Wozeparrot** [[00:35:32](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2132)]
Apparently they're changing that December 2nd.

##### **Geohot** [[00:35:35](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2135)]
Yeah, I really hope so.

##### **Chenyu** [[00:35:37](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2137)]
December 2nd? Okay, I can wait.

##### **Geohot** [[00:35:39](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2139)]
Neon is the frontier now.

##### **Chenyu** [[00:35:52](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2152)]
Okay. Anything else?

##### **Geohot** [[00:35:56](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2156)]
No.

##### **Chenyu** [[00:35:59](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2159)]
Next is my stuff. It's mostly just cleanups and fixups. For studentgrad, we're passing the bulk of the tests now, and everything that doesn't currently pass is slightly annoying. Some of it is speed, and some of it is AFTER and the gradients of AFTER.

##### **Chenyu** [[00:36:31](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2191)]
It's not really an edge case, but finding a principled way to fix it is annoying. So I changed gears today and did some speedups. I did a thing we've wanted to do for a long time: I looked at the past 100 days of CI runs and removed a bunch of tests that never fail or never catch any regressions and just look dumb. That removes like two minutes of CI runtime.

##### **Geohot** [[00:37:06](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2226)]
Great. Yeah.

##### **Chenyu** [[00:37:07](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2227)]
I think anything I removed was not controversial. It's covered by some other test. If we want to be super aggressive, we could probably remove another assortment of tests. Maybe with some time.

##### **Geohot** [[00:37:29](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2249)]
Yeah. I think I saw you added a new test, tiny benchmark.

##### **Chenyu** [[00:37:33](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2253)]
Oh yeah, I also did that. Maybe Nimlgen can comment on the HCQ ones. For AMD machines it's especially slow because of the HCQ2 stuff.

##### **Geohot** [[00:37:53](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2273)]
Yeah. Yeah. I like that. I like that benchmark. I don't know. I mean the NVIDIA ones are crazy and can be like stupidly slow. AMD one is consistently slow.

##### **Chenyu** [[00:38:06](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2286)]
Yeah. I think AMD one just spent like a third of the time in Resizable BAR, even if your bar is already set. So I don't know. Yeah. Another 20% of the time is in the clean up. And because some GC timing issue here and there.

##### **Geohot** [[00:38:31](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2311)]
The clean up is also slow.

##### **Chrism** [[00:38:34](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2314)]
Yeah. Yeah. Yeah. And

##### **Geohot** [[00:38:36](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2316)]
Everyone should be thinking about speed: how we can make things faster, make times better, and make it enjoyable to use.

##### **Chenyu** [[00:38:45](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2325)]
Another minor thing that has a pretty big impact was I changed PARALLEL=1. For now, it doesn't allocate the worker pool. It was doing that for no reason. I just made PARALLEL=1 the same as PARALLEL=0, basically.

##### **Geohot** [[00:39:09](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2349)]
Because on the CI, you always get parallel one.

##### **Chrism** [[00:39:19](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2359)]
Yeah.

##### **Chenyu** [[00:39:24](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2364)]
If you set PARALLEL=1, I updated it to treat it as PARALLEL=0 so it won't allocate a worker pool that only has one worker in it and try to assign work to that single worker.

##### **Geohot** [[00:39:41](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2381)]
Yeah. I mean, I don't know. I like the one zero distinction because that tests the path. We can make zero the default if it's one. But we should still allow, if I explicitly say parallel equals one, it just will create the pool.

##### **Chenyu** [[00:39:59](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2399)]
But we don't want zero to be default, right? It's like, I don't know.

##### **Geohot** [[00:40:04](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2404)]
No, we don't want zero to be the default. But if it, we can say that if it says that the, if it computes that it should be one, it can say actually be zero. See what I mean?

##### **Chenyu** [[00:40:21](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2421)]
Not really.

##### **Geohot** [[00:40:24](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2424)]
I want to still be able to explicitly say parallel equals one and get one worker.

##### **Chenyu** [[00:40:29](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2429)]
Okay.

##### **Geohot** [[00:40:31](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2431)]
But if the CPU count divider says it should be one, use zero.

##### **Chenyu** [[00:40:38](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2438)]
Oh, I see. Okay, sounds good. I'll update that.

##### **Chrism** [[00:40:40](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2440)]
Also, part of the reason that PARALLEL=1 is slow is because it kills the worker every time it runs too many tasks, right?

##### **Chenyu** [[00:40:49](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2449)]
Yeah, there's a limit on everything. There's also some context you need to copy over, or things like that.

##### **Geohot** [[00:40:59](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2459)]
Just keep the worker alive. You want to kill the workers eventually, but one is aggressive. Make that like 100 or something.

##### **Chenyu** [[00:41:06](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2466)]
I think that we have a reasonable number.

##### **Chrism** [[00:41:09](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2469)]
It's like 16 or something, isn't it?

##### **Chenyu** [[00:41:12](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2472)]
Yeah. 16 was a reasonable number. I don't know. I'll update so that we can still specify one. Yeah. And I'm reading this rangeify change. We got a minus-200-line rangeify change. It changes the rangeify algorithm, which looks interesting.

##### **Geohot** [[00:41:39](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2499)]
Yeah, he posted this on Discord earlier.

##### **Geohot** [[00:42:03](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2523)]
He just posted a new one, the latest one. I'm generally supportive of this. I'll need to review it carefully. I don't know who wants to learn about rangeify.

##### **Chenyu** [[00:42:11](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2531)]
It does things differently. I think generally the idea is fine. It's kind of broken, so I will add some more tests. After rebasing, it will show why it's broken.

##### **Geohot** [[00:42:22](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2542)]
Wonderful.

##### **Chenyu** [[00:42:23](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2543)]
But otherwise, I think the direction is good. The old try to assign range and do this and that is kind of sketchy.

##### **Geohot** [[00:42:34](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2554)]
Eventually we want rangeify multi-unification. I'm hoping I can figure out what this should be in studentgrad.

##### **Chenyu** [[00:42:43](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2563)]
OK. Sounds good. OK. I think I will add some tests. My review will probably just making sure all the important features are kept. Given the idea is sound, it just needs to be reviewed. It's still a pretty big change, so we'll see. I can review this.

##### **Geohot** [[00:43:11](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2591)]
Yeah, adding more tests for rangeify is a good idea.

##### **Chenyu** [[00:43:16](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2596)]
Cool. That's my stuff, and we can move on to assembly.

##### **Qazalin** [[00:43:24](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2604)]
Last week I removed 61 lines from x86. This week I'm working on the x86 emulator. Here's a sneak peek.

##### **Qazalin** [[00:43:42](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2622)]
DEV=CPU:X86. This is currently emulating at the instruction level, before any register allocation. You see the add returns a float. There's no ALLOC after it yet. This is generally okay, because emulation is simpler if you leave these value-producing.

##### **Geohot** [[00:44:16](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2656)]
It's a mechanical transformation to go from value-producing to passing in source zero. [unclear]

##### **Geohot** [[00:44:53](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2693)]
Do you want to explain NATIVE?

##### **Qazalin** [[00:44:55](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2695)]
NATIVE is a way we express explicit instruction selection. For example, here in the assembly backend we use a native instruction to add two floats together, and this is backend-specific. NATIVE, by its name, is supposed to be runnable only on the target device, but it has a source zero that is the implementation, a UOp. The idea is that you can verify any backend-specific kernel at the UOp level by removing the NATIVE and rendering source zero. This will allow us to verify the custom kernels on the emulator without opening the device.

##### **Geohot** [[00:45:57](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2757)]
That's native. Actually, I guess we could have a NATIVE without a source that's just void and empty shape, and you could fill in the implementation. Think about the steps in backward compilation, raising from assembly back to UOps.

##### **Geohot** [[00:46:26](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2786)]
Yeah, kind of like that.

##### **Qazalin** [[00:46:29](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2789)]
You can imagine like this assembler first creates a bunch of natives with no shape and void.

##### **Geohot** [[00:46:35](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2795)]
Yeah. And then you can imagine adding the implementation that you could imagine, you know, making a value producing and then you could imagine.

##### **Qazalin** [[00:46:42](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2802)]
Oh, yeah, it's a it's a lifting process to go from a. Yeah. Voids to a value. Yeah.

##### **Geohot** [[00:46:49](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2809)]
And this architecture should allow LLMs to basically take any assembly and produce an entire. You can make emulators in this thing, and then the emulators also give you a path backwards. Instruction selection is a path forwards, right? A reversible compiler.

##### **Qazalin** [[00:47:17](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2837)]
You can also emulate right after instruction selection, which is what this is doing, without emulating your register allocator yet. Just emulate your instruction. So compile to this, which is value producing. I need to still figure out where the value dtype goes for a call. The call should declare its return to value.

##### **Geohot** [[00:47:45](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2865)]
Wait, what?

##### **Qazalin** [[00:47:47](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2867)]
Oh, that's good. The

##### **Geohot** [[00:47:48](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2868)]
calls return dtype is just source zero dtype.

##### **Qazalin** [[00:47:52](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2872)]
But what if your source zero is linear?

##### **Geohot** [[00:47:57](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2877)]
SINK?

##### **Chrism** [[00:47:58](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2878)]
Void?

##### **Geohot** [[00:48:02](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2882)]
Hmm.

##### **Chrism** [[00:48:07](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2887)]
Is it?

##### **Geohot** [[00:48:09](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2889)]
Why wouldn't it be?

##### **Qazalin** [[00:48:11](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2891)]
Is return dtype linear or void? Is it?

##### **Geohot** [[00:48:16](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2896)]
Linear should always have a dtype void. Yeah.

##### **Qazalin** [[00:48:18](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2898)]
Well, imagine lowering the add. It lowers to LINEAR, right? The CALL becomes a LINEAR of A plus B.

##### **Geohot** [[00:48:35](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2915)]
Oh, interesting. Maybe linear should return minus one.

##### **Qazalin** [[00:48:40](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2920)]
Yeah, if you read the diff, there's a four-line function. It's like, "I'm going to return minus one." It gets the dtype of the CALL from the sources.

##### **Geohot** [[00:48:52](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2932)]
Yeah. I mean, yeah, we'll talk about this later. But yeah, linear maybe should return dtype and shape of minus one. Actually, yeah, that's totally right. We can just add that to the construction rules. I didn't add the big dtypes, but I...

##### **Qazalin** [[00:49:21](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2961)]
There's a question of how deeply you want to emulate the execution.

##### **Geohot** [[00:49:29](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2969)]
What do you want to model? [unclear]

##### **Qazalin** [[00:49:44](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2984)]
[unclear]

##### **Geohot** [[00:49:57](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=2997)]
What's that? Well, that's what happens when you remove slop kernels. Funny enough, it also increased the speed of float16 Llama. It's just using BEAM instead of slop kernels.

##### **Qazalin** [[00:50:14](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3014)]
You didn't put slop kernels in the benchmark?

##### **Geohot** [[00:50:17](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3017)]
Nope. Benchmark is slop free. Only slop kernels can have benchmarks with slop kernels.

##### **Chrism** [[00:50:24](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3024)]
kernels.

##### **Geohot** [[00:50:26](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3026)]
Interesting.

##### **Chenyu** [[00:50:30](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3030)]
OK, let's move on. How about RDNA3?

##### **Qazalin** [[00:50:44](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3044)]
I don't think it's being actively worked on.

##### **Chrism** [[00:50:48](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3048)]
I don't think we have anything on RDNA3. Let's get x86 to be good first.

##### **Qazalin** [[00:50:53](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3053)]
The idea is that when we do x86 properly, RDNA3 will be good.

##### **Chenyu** [[00:51:03](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3063)]
OK, sounds good. Next is HCQ2.

##### **Nimlgen** [[00:51:14](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3074)]
Yeah, so I've started on the Chestnut project. I've actually loaded some HCQ2 programs at runtime. That's apparently a bit annoying because it, like Chestnut, has only about 52 kilobytes of free SRAM. So maybe I can shrink the... initial firmware, but it's pretty hard to... I also rewrote the AMD driver with UOps, and it's pretty hard to fit this into the current free SRAM.

##### **Nimlgen** [[00:52:06](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3126)]
So...

##### **Geohot** [[00:52:08](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3128)]
Yeah. I mean, it's 40... Hello. It's, it's 52 kilobytes of code?

##### **Nimlgen** [[00:52:19](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3139)]
Yeah. The compiler is really stupid. It takes a lot of bytes to actually do 64-bit writes into the registers.

##### **Nimlgen** [[00:52:38](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3158)]
So yeah.

##### **Geohot** [[00:52:40](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3160)]
I mean, use calls and... I don't know. Oh, 52 kilobytes.

##### **Qazalin** [[00:52:47](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3167)]
[unclear]

##### **Geohot** [[00:52:52](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3172)]
52 kilobytes sounds like a lot to me, you know?

##### **Nimlgen** [[00:52:56](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3176)]
Yeah, but we have a lot of register writes to boot the GPU.

##### **Geohot** [[00:53:03](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3183)]
Yeah, I mean, you can always chunk it, except...

##### **Nimlgen** [[00:53:07](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3187)]
Yeah, definitely. But that's kind of annoying. So yeah, I'll still look into that.

##### **Geohot** [[00:53:15](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3195)]
Well, wait, also... That thing only has 52k of SRAM? Doesn't it have a lot more SRAM? I guess it can't execute out of that SRAM? Do you actually have code executing out of the SRAM?

##### **Chrism** [[00:53:39](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3219)]
So...

##### **Geohot** [[00:53:41](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3221)]
Can you use the big SRAM?

##### **Nimlgen** [[00:53:45](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3225)]
No, actually there are like two parts of the SRAM, like the high and low. I probably can... I can probably like move the... the original firmware into the high part. So I have more contiguous space.

##### **Nimlgen** [[00:54:04](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3244)]
Something like that. Because I don't remember exact numbers, but it's like... Probably 64 and 16k or something like that.

##### **Chrism** [[00:54:17](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3257)]
Yeah.

##### **Geohot** [[00:54:20](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3260)]
Oh. Interesting. I think it's more actually, because the stock firmware is pretty big. Yeah, and I definitely remember that it takes...

##### **Nimlgen** [[00:54:38](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3278)]
It uses both low and high parts, and they have a special trampoline to call functions from the high part.

##### **Geohot** [[00:54:49](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3289)]
Yeah. I'm also very excited about the move to UOps for the driver because we should be able to boot all the GPUs in parallel, right? Yeah.

##### **Nimlgen** [[00:55:05](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3305)]
In theory, yes. It's still a bit faster, maybe, than the Python implementation. But currently with HCQ2, we cannot execute programs in parallel.

##### **Geohot** [[00:55:23](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3323)]
If I have six GPUs, what do you mean? It's just in a GLOBAL CPU range.

##### **Chrism** [[00:55:33](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3333)]
Yeah.

##### **Geohot** [[00:55:36](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3336)]
That will work. Yeah, I think the other HCQ2 thing to focus on is moving compile stuff into compile.

##### **Chrism** [[00:55:53](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3353)]
Yeah?

##### **Geohot** [[00:55:55](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3355)]
Sorry,

##### **Nimlgen** [[00:55:57](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3357)]
I'll focus on that this week. I also merged the MSM interface. It's a bit slower. I'll look into that more. The LLM said it's because of their driver. They have some different cache management, and there's nothing exposed to userspace to change that.

##### **Chrism** [[00:56:22](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3382)]
So, I mean, Adib said he was happy with it. I wouldn't... Like there are ways off before they ship the mainline kernel. I would not waste too much time messing around with that.

##### **Geohot** [[00:56:35](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3395)]
Okay

##### **Chrism** [[00:56:35](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3395)]
then. It's like it's not urgent for them.

##### **Geohot** [[00:56:39](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3399)]
Yeah, no, I'm glad we have... How much slower is it?

##### **Nimlgen** [[00:56:44](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3404)]
Not much. I mean, in some models... The kernel execution time is about 5% slower or so.

##### **Geohot** [[00:56:56](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3416)]
Yeah, that's fine.

##### **Nimlgen** [[00:56:58](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3418)]
Yeah.

##### **Geohot** [[00:56:59](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3419)]
If it was like 50% slower, we should fix it. But if it's like 5 or 10%, I think that's fine.

##### **Nimlgen** [[00:57:08](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3428)]
For some model it's something like 18 and a half milliseconds for the original one, and like 19.2 for MSM. I don't remember the exact number for the original.

##### **Chrism** [[00:57:26](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3446)]
Just for fun, I've had Neon work on that, and I have it sub-10 milliseconds. Yeah, I mentioned this at lunch. You can run your model a lot faster if you just stick it in an LLM, but there's not so much excitement about that.

##### **Geohot** [[00:57:53](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3473)]
I think it's because it's a huge pain to ship. We need to get the assembly stuff finalized, and then we'll have a Qualcomm assembly backend. Then we'll put the kernels in slop kernels.

##### **Qazalin** [[00:58:04](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3484)]
There's a pending DSP thing too.

##### **Geohot** [[00:58:09](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3489)]
Yeah, we have DSP stuff too. I don't know. I don't think the guy did a particularly good job going through that PR. It's got to get merged. But yeah, that's the main thing we lack. People who can merge things like that.

##### **Chenyu** [[00:58:44](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3524)]
Great. Anything else on HCQ2?

##### **Nimlgen** [[00:58:48](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3528)]
No, that's it for me. This week I'll work on moving more of HCQ2 into scheduling and the tinygrad parts.

##### **Geohot** [[00:59:02](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3542)]
I think 52 kilobytes is a lot of memory. It's a very large program.

##### **Nimlgen** [[00:59:13](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3553)]
I also posted the C-rendered driver. If you've seen it, it looks reasonable. We just have a lot of register writes.

##### **Geohot** [[00:59:27](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3567)]
Where do you post this?

##### **Chrism** [[00:59:30](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3570)]
HCQ drivers.

##### **Nimlgen** [[00:59:33](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3573)]
There was a file to boot the whole 7900.

##### **Geohot** [[00:59:42](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3582)]
Hmm. Yeah, this looks like a reasonable GPU driver. It smells good.

##### **Chenyu** [[01:00:06](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3606)]
Anything else for the meeting? Is comma happy? I think comma is busy with sales.

##### **Chrism** [[01:00:11](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3611)]
Yeah, comma is pretty busy, but they mentioned, or at least Shane is complaining about Kimi stalling a whole bunch. Like he says, if you try and submit two requests in parallel, one of them will stall. He has some theories about how to fix this, and I don't know. I mean, do we want to? I mean, he has SSH access. Should we just tell him we can try his? I think

##### **Chenyu** [[01:00:36](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3636)]
George said that already somewhere.

##### **Geohot** [[01:00:38](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3638)]
Yeah. I gave him SSH to the machines. He could, you know... If he breaks them, he loses his SSH access.

##### **Chrism** [[01:00:48](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3648)]
All right. Sounds good.

##### **Geohot** [[01:00:51](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3651)]
But, you know, I'll try with him, seeing if he can, like, mess with the SGLang. I'm just using the SGLang... This isn't custom. This is, like, literally how they recommend you run it.

##### **Chrism** [[01:01:02](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3662)]
Yeah.

##### **Geohot** [[01:01:03](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3663)]
So... Okay. Sounds good.

##### **Chenyu** [[01:01:12](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3672)]
So, George, you will be out for the next meeting?

##### **Geohot** [[01:01:17](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3677)]
Yes. Yes, I'll be out for the next two meetings. Sounds good.

##### **Chenyu** [[01:01:23](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3683)]
Okay. I think... Oh, sorry. Go ahead.

##### **Geohot** [[01:01:26](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3686)]
Just on B1TG's update: don't worry so much about faster kernels. Just make sure it links to slop kernels correctly and that we get all the nice stuff in from DeepSeek V4.1 and everything. You're welcome to change slop kernels too, but we now have a clear separation between the kernels and the implementations. Well, sounds good.

##### **Chenyu** [[01:02:02](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3722)]
Anything else for this meeting?

##### **Chrism** [[01:02:07](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3727)]
No.

##### **Geohot** [[01:02:09](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3729)]
Okay.

##### **Chenyu** [[01:02:12](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3732)]
I think we'll still keep this meeting time for the next two weeks. It seems to work for everyone. We'll discuss if we need to change it later.

##### **Chenyu** [[01:02:24](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3744)]
And that's it for this one. Thanks, everyone. Happy holiday. Happy trip. See you.

##### **Geohot** [[01:02:33](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3753)]
And see you later. Thanks.

##### **Chrism** [[01:02:36](https://www.youtube.com/watch?v=2hV3Y0TMPd0&t=3756)]
Bye.
