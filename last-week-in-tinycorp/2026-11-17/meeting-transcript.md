# 2026-11-17 Meeting

### Meeting Agenda

**Time:** new meeting #46, 11/17 12pm Hong Kong time
- company update
- llm service
- machines
- hcq2, drivers
- assembly
- Ops.EXTERN, course
- after effect LOOP
- bounties, comma, other issues


### Audio

[Youtube Link](https://www.youtube.com/watch?v=jPGI-sEdddk)

### Highlights

- **[Company Update](#geohot-000044)**: Batch two of the MI300X machines has launched and customer orders ship soon (quoted at 1-8 weeks, which Geohot wants shortened). A large GPU binning project found about half the GPUs work to some extent, and roughly 30% of those are fully good.
- **[LLM Service](#geohot-000223)**: The Qwen 3.8 Flash license doesn't allow commercial inference, so tinygrad is launching a free, non-commercial hobbyist service. Charging would start once a Qwen 4 release with a friendlier license arrives.
- **[API Limits & GitHub Login](#geohot-000643)**: Each box serves about 30 agents. Public API keys are capped at two sessions and a dollar, employees are unlimited, and everyone (including comma) will log in with GitHub so token usage can be tracked.
- **[Machines](#chrism-001451)**: Iris is usable for everyone, with a bigger CPU type and more RAM on the 7900 XTX VMs. Open items are a faster, easier-to-update RAID solution, power for tinybox Pro Blackwells, and CI runners that lost their 10-gig cards.
- **[Stateless Infrastructure](#geohot-002043)**: Geohot wants machines with no boot drives that PXE boot, keeping state only on a RAID that is easy to regenerate. The goal is a "real cloud provider" with minimal state.
- **[CI Migration](#geohot-002825)**: Master CI will move from GitHub Actions onto tinygrad's own hardware, to be changed right after the meeting. The team will take full responsibility for outages.
- **[HCQ2 & Drivers](#nimlgen-003024)**: TCC is merged for HCQ2 and is the default in CI, much faster but x86-only (Macs produce Mach-O instead of ELF; Geohot suggests LLVM there). VFIO is merged too, and only the udev rules are missing from the image before admin capabilities can be dropped.
- **[Kimi Speed](#nimlgen-003243)**: A live Kimi server running off disk reaches about 600 tokens/s prefill (still compute-bound) and about 35 tokens/s decode, sometimes 48.
- **[Chestnut Project](#nimlgen-003631)**: Nimlgen will move CPU host programs onto the Chestnut's 8051 CPU. Geohot expects this to cut about 5 ms of latency from comma's models.
- **[Network-Attached GPUs](#geohot-003921)**: Geohot's vision is GPUs with network ports, distributing programs up front and leaving only high-bandwidth GPU communication during a job. He argues a low-latency command path is only needed when driving from a CPU, which is why HCQ2 matters.
- **[Assembly](#qazalin-004145)**: x86 cleanups are merged, RDNA3 is already on the new CALL/ASM op, and x86 should switch to the new CALL style by end of week. Register dtypes were debated (x86 goes up to 512 bits), and the team settled on a shaped u32 for now.
- **[Ops.EXTERN](#geohot-005350)**: EXTERN is a globally scoped PARAM. Tensor.export converts buffers and variables into EXTERNs to produce exportable UIR, and Tensor.run executes it, splitting tinygrad into frontend, compiler and runtime.
- **[RANGE Axis Default](#chenyu-010050)**: Chenyu proposes defaulting RANGE axes to LOOP (sequential) instead of WEAK to avoid silent race conditions, with internal uses explicitly annotated. Geohot supports it.
- **[PRs & Bounties](#geohot-010829)**: Contributors should close PRs unless highly confident they're worth a person's time. Geohot says bounties are "kind of over with AI" and he won't pay for slop that only technically meets the definition.

### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=jPGI-sEdddk&t=0)]
I just posted in MLPerf. The result is out, although they make it even harder to navigate the results. But all tinygrad's results are there, so it's good.

##### **Wozeparrot** [[00:00:13](https://www.youtube.com/watch?v=jPGI-sEdddk&t=13)]
It's supposed to be easier to navigate. They're pushing it very hard during the meeting, saying that the new UI is supposed to be better.

##### **Chenyu** [[00:00:20](https://www.youtube.com/watch?v=jPGI-sEdddk&t=20)]
I mean, it cannot be better than just a sheet that you can filter, and now you cannot. So...

##### **Geohot** [[00:00:30](https://www.youtube.com/watch?v=jPGI-sEdddk&t=30)]
I don't know. I mean, whatever.

##### **Chenyu** [[00:00:37](https://www.youtube.com/watch?v=jPGI-sEdddk&t=37)]
Cool. Let's get started. We'll start with the company update.

##### **Geohot** [[00:00:44](https://www.youtube.com/watch?v=jPGI-sEdddk&t=44)]
So yeah, we launched batch two of the MI300X machines. We're going to also start shipping customer orders soon. Sorry if you're a customer order. That has taken a while. We say one to eight weeks. But I want to get that down. We should not be taking eight weeks to build computers. We have all the parts. You know, we just have a labor shortage. We need those Optimus robots. Yeah, we've been doing the biggest thing we've been doing is the massive binning project of the GPUs. This gives you an idea of how many work and how many don't work. So about half of them work to some extent. And then probably within that half, probably like 30% are like totally good. And then the green ones are totally good. And the other colors have other issues. Yeah. So I think that's kind of the main thing. I see LLM service is the next thing, so we can put that in the company update. But yeah, I guess we can get to that next.

##### **Chenyu** [[00:02:15](https://www.youtube.com/watch?v=jPGI-sEdddk&t=135)]
Good. Okay. Next is service. What are we launching again?

##### **Geohot** [[00:02:23](https://www.youtube.com/watch?v=jPGI-sEdddk&t=143)]
Well, okay. So it turns out that Qwen 3.8 Flash, we're not actually allowed under the license to use for a commercial inference service. So we're going to launch a non-commercial hobbyist inference service where you can get some free Qwen 3.8 Flash tokens. I want everything set up to the point that we have money, but it's [unclear] bucks, to make sure we comply with the Qwen license. I think Qwen4 comes out and it probably won't have that license, and then we can start charging money. But it is free while it is Qwen 3.8 Flash.

##### **Geohot** [[00:03:09](https://www.youtube.com/watch?v=jPGI-sEdddk&t=189)]
Yeah. So, Wozeparrot, any updates on that?

##### **Wozeparrot** [[00:03:15](https://www.youtube.com/watch?v=jPGI-sEdddk&t=195)]
Yeah, I just deployed and it broke everything. So I'm fixing it.

##### **Geohot** [[00:03:22](https://www.youtube.com/watch?v=jPGI-sEdddk&t=202)]
Deployed what?

##### **Wozeparrot** [[00:03:24](https://www.youtube.com/watch?v=jPGI-sEdddk&t=204)]
Router. Token router.

##### **Geohot** [[00:03:25](https://www.youtube.com/watch?v=jPGI-sEdddk&t=205)]
Okay.

##### **Wozeparrot** [[00:03:29](https://www.youtube.com/watch?v=jPGI-sEdddk&t=209)]
Yeah, I'll focus on fixing it, but I'll say kind of where we are. I migrated metrics over. We're on a new metrics database because InfluxDB 3 is really bad. So we're on VictoriaMetrics now. It is actually significantly simpler than Influx, and we can query it just with standard MetricsQL that Prometheus uses. That's pretty good.

##### **Chrism** [[00:04:01](https://www.youtube.com/watch?v=jPGI-sEdddk&t=241)]
Can confirm that it's better than what it was before.

##### **Wozeparrot** [[00:04:05](https://www.youtube.com/watch?v=jPGI-sEdddk&t=245)]
Yeah. It's a lot nicer to query. It's way faster too.

##### **Geohot** [[00:04:14](https://www.youtube.com/watch?v=jPGI-sEdddk&t=254)]
Yeah, it was crazy how slow the other one was.

##### **Wozeparrot** [[00:04:23](https://www.youtube.com/watch?v=jPGI-sEdddk&t=263)]
And then, for token router, I added a way to connect to VMs. I added a token-router user to Iris. If you make VMs under that user, you can dynamically add them. I posted about how to do this in employees-info.

##### **Geohot** [[00:04:43](https://www.youtube.com/watch?v=jPGI-sEdddk&t=283)]
Yeah, that makes sense.

##### **Wozeparrot** [[00:04:45](https://www.youtube.com/watch?v=jPGI-sEdddk&t=285)]
SSH URI, and then we'll open a tunnel to the VM.

##### **Geohot** [[00:04:50](https://www.youtube.com/watch?v=jPGI-sEdddk&t=290)]
Cool.

##### **Chrism** [[00:04:52](https://www.youtube.com/watch?v=jPGI-sEdddk&t=292)]
Yeah. We'll have a user.

##### **Geohot** [[00:04:56](https://www.youtube.com/watch?v=jPGI-sEdddk&t=296)]
Yeah, we'll have some autoscaler service running somewhere. We should have seven boxes. And we can like scale up to six of them. If we have demand. We'll make sure we have plenty of demand at launch. And then we'll see if anyone actually uses it. And yeah. So I want people to be able to create accounts with GitHub and then manage API keys.

##### **Wozeparrot** [[00:05:22](https://www.youtube.com/watch?v=jPGI-sEdddk&t=322)]
Yeah, and we'll look at auth this week before Friday for launch. And metrics, I just need to port over to the new metrics stack.

##### **Geohot** [[00:05:32](https://www.youtube.com/watch?v=jPGI-sEdddk&t=332)]
Cool. Yeah. I want to give, I want to do auth and I basically want to give everyone like a fake dollar when they create the GitHub account. We had to do billing to prevent abuse. Yeah, and I think we can also just toggle signups on and off.

##### **Wozeparrot** [[00:05:52](https://www.youtube.com/watch?v=jPGI-sEdddk&t=352)]
We'll see. Do you know if your Qwen servers have my cached-tokens PR?

##### **Geohot** [[00:06:00](https://www.youtube.com/watch?v=jPGI-sEdddk&t=360)]
If it's in master, then yes. Okay. They're, they're, they're constantly staying up to date with master.

##### **Wozeparrot** [[00:06:11](https://www.youtube.com/watch?v=jPGI-sEdddk&t=371)]
Yeah, because I do rely on the backend to report how many cached tokens.

##### **Geohot** [[00:06:16](https://www.youtube.com/watch?v=jPGI-sEdddk&t=376)]
Yeah. That makes sense. Yeah. Do we think there do we think there's demand for free flash tokens?

##### **Wozeparrot** [[00:06:40](https://www.youtube.com/watch?v=jPGI-sEdddk&t=400)]
I mean, I think there's always demand for free tokens.

##### **Geohot** [[00:06:43](https://www.youtube.com/watch?v=jPGI-sEdddk&t=403)]
Yeah. So each box can serve about 30 users, or 30 agents. Can we also limit the number of connections per API key?

##### **Wozeparrot** [[00:06:56](https://www.youtube.com/watch?v=jPGI-sEdddk&t=416)]
For API key? Yeah, that's easy to add.

##### **Geohot** [[00:06:59](https://www.youtube.com/watch?v=jPGI-sEdddk&t=419)]
Yeah, I think we want to limit that to like, but again, these should be dynamically toggleable. For all the public API keys, they're going to be limited to two sessions and a dollar. For employees, they're all unlimited. And I want to move everybody here, and I want to move comma, not just using one tinycorp key and one comma key. I want everybody here to log in with their GitHub account, so we can track token usage. We are our own inference provider.

##### **Wozeparrot** [[00:07:34](https://www.youtube.com/watch?v=jPGI-sEdddk&t=454)]
On LLM serving, I've noticed that Kimi gets really bad sometimes.

##### **Geohot** [[00:07:42](https://www.youtube.com/watch?v=jPGI-sEdddk&t=462)]
Yeah, so okay, the Kimis have bugs. There's bugs in SGLang. I improved it a bit last night. So there's two bugs in SGLang Kimi that are open on the issues that have not been fixed. So sometimes when it gets really bad, it's the server restarting. It takes like 20 minutes to restart. It's been a lot better now that we have two.

##### **Wozeparrot** [[00:08:08](https://www.youtube.com/watch?v=jPGI-sEdddk&t=488)]
It's not the time. It's just it constantly fails tool calls.

##### **Qazalin** [[00:08:14](https://www.youtube.com/watch?v=jPGI-sEdddk&t=494)]
Yeah, I've seen that.

##### **Geohot** [[00:08:15](https://www.youtube.com/watch?v=jPGI-sEdddk&t=495)]
Yeah, I've noticed this too. When's the last time? I fixed that last night.

##### **Wozeparrot** [[00:08:21](https://www.youtube.com/watch?v=jPGI-sEdddk&t=501)]
Okay, this was a while ago. I switched back to GLM-5.3 because I got really annoyed by that.

##### **Geohot** [[00:08:26](https://www.youtube.com/watch?v=jPGI-sEdddk&t=506)]
Yeah, so it should be fixed. What it was was... I saw it occasionally inserting weird tokens. And what Fable said the fix was for that was to have top-p basically only take the top 5% of tokens to sample from. There were long-tail issues. I don't know. Let me know if you think it's fixed. If it's not fixed, I would totally just believe that there's bugs in that SGLang streaming, because there's other bugs. Also, for GLM-5.3, I've put up TS5 as well. I used the enroll stuff to enroll it. Let me see if it's up right now. So you can use GLM53-TS5. And I want to eventually migrate to that so that we can use AMD1 for more GPU binning. This is running on whale. And then anything that anyone here can use Qwen tokens for, we are going to have many, many, many Qwen 3.8 Flash tokens. So we can support about 30 users per box at like 60 tokens a second.

##### **Chrism** [[00:10:04](https://www.youtube.com/watch?v=jPGI-sEdddk&t=604)]
So comma mentioned that they do use Qwen for DM ground truth. But this is not the same Qwen, I think. But if there's any interest in running that Qwen, they're excited about that.

##### **Geohot** [[00:10:19](https://www.youtube.com/watch?v=jPGI-sEdddk&t=619)]
Oh, they should use this Qwen because I think they'll find it is a lot better.

##### **Chrism** [[00:10:23](https://www.youtube.com/watch?v=jPGI-sEdddk&t=623)]
That's true.

##### **Geohot** [[00:10:24](https://www.youtube.com/watch?v=jPGI-sEdddk&t=624)]
This Qwen is a shit ton better than what they're using.

##### **Chrism** [[00:10:29](https://www.youtube.com/watch?v=jPGI-sEdddk&t=629)]
I would imagine that, yeah.

##### **Geohot** [[00:10:30](https://www.youtube.com/watch?v=jPGI-sEdddk&t=630)]
Yeah, images are supported too. Images are supported in both Qwen and GLM Flash. And I'm running Pokemon at scale right now. And it's not the top open model at Pokemon, but it's close. It's not as good as Kimi, but.

##### **Wozeparrot** [[00:10:48](https://www.youtube.com/watch?v=jPGI-sEdddk&t=648)]
I'm hoping Qwen 4 is better because so far with Qwen 4 Max, it's not that great.

##### **Geohot** [[00:10:55](https://www.youtube.com/watch?v=jPGI-sEdddk&t=655)]
You've tried Qwen 4 Max? Or just what people say?

##### **Wozeparrot** [[00:11:00](https://www.youtube.com/watch?v=jPGI-sEdddk&t=660)]
Just what people say, and then a couple of tokens.

##### **Geohot** [[00:11:05](https://www.youtube.com/watch?v=jPGI-sEdddk&t=665)]
Yeah, yeah. I mean, hopefully Qwen 4 Flash is at least an improvement over Qwen 3.5, 3.8 Flash.

##### **Chenyu** [[00:11:18](https://www.youtube.com/watch?v=jPGI-sEdddk&t=678)]
Is it served with SGLang?

##### **Geohot** [[00:11:22](https://www.youtube.com/watch?v=jPGI-sEdddk&t=682)]
No, tinygrad.

##### **Chenyu** [[00:11:28](https://www.youtube.com/watch?v=jPGI-sEdddk&t=688)]
Oh, served with master tinygrad? Which tinygrad?

##### **Geohot** [[00:11:31](https://www.youtube.com/watch?v=jPGI-sEdddk&t=691)]
No, not master tinygrad. The branch is the red Qwen Flash branch. I've had a little agent swarm working on it for a while.

##### **Chenyu** [[00:11:44](https://www.youtube.com/watch?v=jPGI-sEdddk&t=704)]
I see.

##### **Geohot** [[00:11:49](https://www.youtube.com/watch?v=jPGI-sEdddk&t=709)]
So, yeah, there's a lot of stuff. Yeah, yeah. It's kind of massive. But most of it is actually just in kernels.

##### **Chrism** [[00:12:02](https://www.youtube.com/watch?v=jPGI-sEdddk&t=722)]
Okay.

##### **Geohot** [[00:12:04](https://www.youtube.com/watch?v=jPGI-sEdddk&t=724)]
So, yeah, when we get to my stuff, that's the other big thing I've been working on, fixing this. So it'll be master plus kernels. That's what we want to get to.

##### **Chenyu** [[00:12:16](https://www.youtube.com/watch?v=jPGI-sEdddk&t=736)]
Oh, I see. It's mostly just those kernels that are different.

##### **Geohot** [[00:12:21](https://www.youtube.com/watch?v=jPGI-sEdddk&t=741)]
Yeah, yeah, yeah. It mostly.

##### **Chenyu** [[00:12:23](https://www.youtube.com/watch?v=jPGI-sEdddk&t=743)]
Some tinygrad changes. Interesting. Okay.

##### **Geohot** [[00:12:27](https://www.youtube.com/watch?v=jPGI-sEdddk&t=747)]
There's tinygrad changes that I think mostly can be removed. The main things that matter are the whole chunks of kernels.

##### **Chenyu** [[00:12:41](https://www.youtube.com/watch?v=jPGI-sEdddk&t=761)]
Okay.

##### **Geohot** [[00:12:43](https://www.youtube.com/watch?v=jPGI-sEdddk&t=763)]
There's like 20,000 lines of kernels.

##### **Chenyu** [[00:12:50](https://www.youtube.com/watch?v=jPGI-sEdddk&t=770)]
Okay. Sounds good.

##### **Geohot** [[00:13:07](https://www.youtube.com/watch?v=jPGI-sEdddk&t=787)]
Yeah. We'll figure out a bit of an on-call strategy, too. We should really try to keep this up. We need to make sure this is something that a bunch of people here can maintain. We're serving the good models for us and comma, and we're serving the models for free for everybody. I feel like there is not a good... Like, where would you go right now if you wanted a free model?

##### **Wozeparrot** [[00:13:46](https://www.youtube.com/watch?v=jPGI-sEdddk&t=826)]
You can run it locally.

##### **Geohot** [[00:13:49](https://www.youtube.com/watch?v=jPGI-sEdddk&t=829)]
Well, you can run it locally, but you're not going to really be able to run Qwen 3.8 Flash. You're not going to be able to really run Qwen Flash here locally. Like, the best things you could...

##### **Wozeparrot** [[00:14:01](https://www.youtube.com/watch?v=jPGI-sEdddk&t=841)]
I don't know. Other people can.

##### **Geohot** [[00:14:05](https://www.youtube.com/watch?v=jPGI-sEdddk&t=845)]
On your Strix Halo?

##### **Wozeparrot** [[00:14:06](https://www.youtube.com/watch?v=jPGI-sEdddk&t=846)]
Yeah.

##### **Geohot** [[00:14:08](https://www.youtube.com/watch?v=jPGI-sEdddk&t=848)]
Yeah, if you have the Strix Halo and a ton of RAM, then you might be able to run Qwen 3.8 Flash that way. But, I mean, for most people, even if you have a GPU, the Flash is a lot better than the 27B. Cool.

##### **Chenyu** [[00:14:32](https://www.youtube.com/watch?v=jPGI-sEdddk&t=872)]
Okay. So we will launch and just see how many people use this.

##### **Geohot** [[00:14:40](https://www.youtube.com/watch?v=jPGI-sEdddk&t=880)]
Yeah. Okay, sounds good.

##### **Chenyu** [[00:14:44](https://www.youtube.com/watch?v=jPGI-sEdddk&t=884)]
Now we can move on to the machines. This is for Chris.

##### **Chrism** [[00:14:51](https://www.youtube.com/watch?v=jPGI-sEdddk&t=891)]
Yep. Yeah, so hopefully Iris is usable for everyone. I'm looking into how we can have a better solution for the RAID array to make it both faster and also easier to... update the weights on. But, yeah, so if there's any... if you're running into any issues or anything that is more difficult to do on the VMs than it was to do on real hardware, let me know. We have the big CPU type now, as well as a bit more RAM on the... 7900 XTX VMs. Yeah, that's the main thing. Also moved all those computers around. We have to think a little bit about if we want to have enough power to provision tinybox Pro Blackwells. Yeah, that's one thing. Oh, yeah, that's the photo I took. Yeah.

##### **Geohot** [[00:16:05](https://www.youtube.com/watch?v=jPGI-sEdddk&t=965)]
Yeah.

##### **Chrism** [[00:16:09](https://www.youtube.com/watch?v=jPGI-sEdddk&t=969)]
That's mostly what's going on.

##### **Geohot** [[00:16:12](https://www.youtube.com/watch?v=jPGI-sEdddk&t=972)]
So, yeah, I mean, we need to find some better way to synchronize the RAID drives. Is it easy for you to add R7 and G3 to the pool?

##### **Chrism** [[00:16:22](https://www.youtube.com/watch?v=jPGI-sEdddk&t=982)]
Yeah, yeah, I can add those.

##### **Geohot** [[00:16:25](https://www.youtube.com/watch?v=jPGI-sEdddk&t=985)]
Yeah, I had annoying stuff to do it, but if you have scripts to do it, it's a lot better. We should have procedures, because it's annoying. You've got to make sure the IOMMU is on.

##### **Chrism** [[00:16:35](https://www.youtube.com/watch?v=jPGI-sEdddk&t=995)]
Yeah, I'll write down a list of steps. You're right, I should have written all that down. The one thing that I didn't realize until this morning was that previously all the runners in the Incus pool had a 10-gig card, and now they don't. So this may have some implications for CI on the runners that download stuff. Um...

##### **Geohot** [[00:17:07](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1027)]
I'm just pointing out. Oh, I see. Uh... Yeah. Can the 100 gig work for internet?

##### **Chrism** [[00:17:17](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1037)]
Yep. Yeah, I can set that up. Um, that's another thing that I have been working on, but it's kind of been slow progress is getting everything moved over onto our router. But that 100 gig, there's no reason we can't have that be downstream of our router. Um... Yeah. So I was thinking of just having that 100-gig network connected to the router, routable to the main sort of untrusted network.

##### **Geohot** [[00:17:43](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1063)]
Yeah, I mean, that, that, that seems good. And then like everything that's plugged into that 100 gig switch.

##### **Chrism** [[00:17:48](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1068)]
Yeah.

##### **Geohot** [[00:17:48](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1068)]
Everything, like we...

##### **Chrism** [[00:17:50](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1070)]
Yeah, I was just a little nervous about...

##### **Geohot** [[00:17:51](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1071)]
Oh, sorry. Go ahead.

##### **Chrism** [[00:17:52](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1072)]
I was just saying I was a little nervous about taking a whole bunch of stuff offline as I slowly move stuff over. So I was going to start moving over BMCs. And then if that all works, then I'll move over everything else. We should be able to split the network such that the untrusted network can't reach the BMC, which would be good.

##### **Geohot** [[00:18:13](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1093)]
Yeah, that's good. I mean, just, you know, everything here that we're doing is like, I want to be basically a real cloud provider and a real token provider.

##### **Chrism** [[00:18:24](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1104)]
Yeah.

##### **Geohot** [[00:18:25](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1105)]
Um, I think that like this infrastructure for what we do next is pretty much like, like non-negotiable. Where I see things going is, when we want to do large-scale tinygrad training jobs, these machines will continue to run a 16-gig Linux VM. Who cares?

##### **Chrism** [[00:18:48](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1128)]
Yeah.

##### **Geohot** [[00:18:49](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1129)]
Um, yeah. And these pass-throughs seem to not impact performance at all, which is what we expect, right?

##### **Chrism** [[00:18:56](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1136)]
Yes. Yeah. Yeah. And I think I have found a way to have very low overhead with the NVMes as well.

##### **Geohot** [[00:19:05](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1145)]
Great. Yeah, for some of the machines, I think we will end up just passing through the NVMes as well. But that's always an option. I don't think we should do that whenever we have multiple sharing. But when we get to our training cluster, it's all going to be the exact same CI infrastructure.

##### **Chrism** [[00:19:26](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1166)]
Right.

##### **Geohot** [[00:19:27](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1167)]
And when we have...

##### **Chrism** [[00:19:28](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1168)]
Yeah. Yeah. And... Oh, sorry.

##### **Geohot** [[00:19:32](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1172)]
Uh, go ahead.

##### **Chrism** [[00:19:33](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1173)]
I was going to say, we mentioned this, I don't remember which channel, but maybe making a new image for the VM hosts. That is probably worth doing because I think there's a lot of junk on the image right now. We run some old version of QEMU because that's the one that comes when you install it with Ubuntu, and stuff like this. It's probably worth fixing it all up.

##### **Geohot** [[00:20:05](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1205)]
Yeah. A new image for the VM hosts. I mean, do we even really need boot drives?

##### **Chrism** [[00:20:12](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1212)]
I mean, we need somewhere to store Incus, right? Like the QEMU binary. There's somewhere you need to store this data. I guess it could be a partition on the RAID.

##### **Geohot** [[00:20:27](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1227)]
One gig of RAM?

##### **Chrism** [[00:20:30](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1230)]
Well, but non-volatile. It needs to store...

##### **Geohot** [[00:20:34](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1234)]
Why?

##### **Chrism** [[00:20:36](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1236)]
Just PXE boot it?

##### **Geohot** [[00:20:38](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1238)]
Yeah.

##### **Chrism** [[00:20:39](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1239)]
Uh, yeah. Yeah. That's probably fine. I can look into that.

##### **Geohot** [[00:20:43](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1243)]
I mean, yeah, I just, I just really don't like the idea of state, right? My ideal thing is that all these computers just don't have boot drives. They PXE boot. We have state on the RAID, but the state on the RAID has some simple way to regenerate it once you're fully booted into Linux and everything. Yeah.

##### **Chrism** [[00:21:08](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1268)]
Yeah.

##### **Geohot** [[00:21:10](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1270)]
But yeah, no, I mean, I also, I also liked the idea of, uh, you know, save money on boot drives. Yeah. Yeah.

##### **Chrism** [[00:21:17](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1277)]
Yeah, yeah. This is the...

##### **Geohot** [[00:21:19](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1279)]
Boot drives are janky on the USB. They fail. It would be great if these machines just PXE booted, and then sure, we have RAID arrays of storage.

##### **Chrism** [[00:21:28](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1288)]
Yeah.

##### **Geohot** [[00:21:28](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1288)]
But those are easy to regenerate. So I think that's where we want to go with our cloud.

##### **Chrism** [[00:21:36](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1296)]
Yeah, I mean, I like the 100-gig...

##### **Geohot** [[00:21:38](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1298)]
Oh, sure. Yeah, go ahead.

##### **Chrism** [[00:21:39](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1299)]
I was gonna say, I like the hundred gig goals as well, because those 10 gig cards, those Marvell cards just seem really flaky. I, uh, I, I, I didn't know that Marvell made crappy cards, but now I know.

##### **Geohot** [[00:21:51](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1311)]
I mean, we can buy more cards. I'm sure they're not expensive.

##### **Chrism** [[00:21:54](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1314)]
Well, but the a hundred gig, at least we know they work quite well.

##### **Geohot** [[00:22:00](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1320)]
Yeah. Um, but yeah, no. So like what we should be thinking about, like where we basically want to go, uh, with all of this stuff is like, you know, our LLM provider and our, our, our cloud provider is like, we can imagine our own form of RSI. All right. We can imagine our own form of, you know, these things kind of sitting there and figuring out how to organize themselves. And we want it to be really easy to do things like scale up resources.

##### **Chrism** [[00:22:31](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1351)]
Right.

##### **Geohot** [[00:22:32](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1352)]
Right. Yeah. Yeah.

##### **Chrism** [[00:22:35](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1355)]
That's a fun way of thinking of it.

##### **Geohot** [[00:22:36](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1356)]
Yeah. Right. Like, and this is why we want these like hyper fast. I mean, like when you boot machines on AWS or DigitalOcean, it takes forever.

##### **Chrism** [[00:22:45](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1365)]
Yeah.

##### **Geohot** [[00:22:46](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1366)]
Minutes, right? We want these hyper-fast-to-boot VMs that are real VMs that really pass through the hardware, so there's zero overhead. And then one of the things that should be built into our VM image is we should have Pi preinstalled, with an API key. Yeah.

##### **Chrism** [[00:23:08](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1388)]
Yeah. These things are easy to do. Um, yeah, yeah.

##### **Geohot** [[00:23:14](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1394)]
I mean like, sorry.

##### **Chrism** [[00:23:18](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1398)]
Oh, go ahead. If your, if your API key is associated with your SSH key. Right.

##### **Geohot** [[00:23:24](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1404)]
Yeah. I've been playing with these agent swarm things, and they are kind of starting to work. So you could imagine an agent swarm accessing all the CI boxes and operating.

##### **Chrism** [[00:23:37](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1417)]
Yeah. Hopefully not crashing all the soft-bricking all the GPUs.

##### **Geohot** [[00:23:43](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1423)]
Well, yeah, we've got to figure out what we're going to do about that. It seems like humans do this just as much too. Yeah, yeah. Yeah.

##### **Chrism** [[00:23:55](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1435)]
Yeah, I'll think about this. One of the things I have been thinking about is it may not make sense. Incus seems quite nice in a lot of ways, but there may be tools that make a little bit more sense if we're not going to have Linux hosts. Because there's QEMU. I looked into this a lot to try and get our VMs to boot really, really fast. This was one thing I was looking at, just because it's nice to have CI start up really fast. But QEMU kind of struggles to do this in the way that you would hope. It seems to be maybe just such a massive project that it's gotten stuck in having a lot of legacy code. As a result, it's difficult for it to modernize in a way to be able to spin up VMs super fast. So I might read a little bit about what sort of alternative hypervisors people use.

##### **Geohot** [[00:24:54](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1494)]
Yeah, yeah, I'm fine with it being hypervisor. But in general, every time we get rid of state, it's a really big win. State is incredibly bad. Keeping state synchronized is super hard.

##### **Chrism** [[00:25:16](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1516)]
Yeah, that's mostly it. I was looking at also, maybe if we can get NVMe either through, like, well, I was looking at QEMU NVMe, such that the NVMe driver would even work in the VMs, which would be nice. There's NVMe-oF, where all the NVMe verbs should work just fine. But rather than being over PCI, it's over RDMA or TCP or what have you. Or you can just emulate the device.

##### **Geohot** [[00:25:50](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1550)]
The problem, you have to consider your VM occupancy. If you have multiple VMs on the computer, how can you have the NVMe driver in the VMs?

##### **Chrism** [[00:26:07](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1567)]
So if you use NVMe-oF, it looks like there's a way to do that, such that, you know, all your VMs are read-only on the drive. And then the host can control the contents of the drive.

##### **Geohot** [[00:26:19](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1579)]
Oh, okay, cool. Yeah. Yeah, as long as they can, as long as we can enforce the, yeah, but like, I even worry about that. Like, even if they are read-only, what happens when the file system changes underneath them?

##### **Chrism** [[00:26:34](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1594)]
Yeah, I think it should be possible to do this intelligently. You basically just need a garbage-collecting sort of thing. For instance, if you're on Linux and you move a file while it's still open, or if you try and remove a file that's still in use, it keeps the data around. A filesystem knows to keep it around until you're done with the file.

##### **Geohot** [[00:27:03](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1623)]
Yeah, but the guest filesystem can't keep that around, right? If the guest has access to the file...

##### **Chrism** [[00:27:08](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1628)]
No, but it feels like your NVMe drive should be able to do this, right? Like you're referring to this region. And then you just...

##### **Geohot** [[00:27:19](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1639)]
Oh, I don't think so.

##### **Chrism** [[00:27:22](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1642)]
Anyway, this is, this is I think off topic.

##### **Geohot** [[00:27:25](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1645)]
Yeah, whatever. I think what we're doing with the NVMes now is mostly fine. If there's a way we can get a little more speed, that's good. But the other option is just going to be that we're going to pass the NVMes through and let tinygrad use them, like the Kimi Box.

##### **Chrism** [[00:27:38](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1658)]
Yeah, yeah, yeah, that makes sense.

##### **Chenyu** [[00:27:47](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1667)]
Any comments? CI failures or flakiness?

##### **Chrism** [[00:27:55](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1675)]
I, so I've seen a lot of these issues. I mean, a lot of them, a lot of the recent ones have been on GitHub. I'll look, look a little bit more into, into what I can do about the other stuff. But,

##### **Chenyu** [[00:28:10](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1690)]
Or I mean, I don't, I don't know if, if you want any kind of reporting because I feel I have hit some kind of error every day, but every time I just click retry and it will work fine.

##### **Geohot** [[00:28:25](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1705)]
You know what? I'm ready. I am ready. We want to just move master to our stuff.

##### **Chrism** [[00:28:33](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1713)]
Yeah. Yeah. That would, at the very least, the stupid autogen thing that fails every once in a while, just because GitHub fails to connect the internet to the VM would not happen anymore.

##### **Geohot** [[00:28:43](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1723)]
Yeah, let's move master to our stuff. And then every outage, every failure is our fault.

##### **Chrism** [[00:28:49](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1729)]
Yeah.

##### **Geohot** [[00:28:50](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1730)]
Yeah. Sounds good. I mean, we can't, we can't control GitHub, the spiky internet, but we can definitely, yeah, move, move everything.

##### **Chenyu** [[00:28:58](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1738)]
What do you mean by that? Do I need to change anything? Yeah.

##### **Geohot** [[00:29:02](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1742)]
No, master right now is running on GitHub Actions, but we can just run master on our stuff.

##### **Chenyu** [[00:29:09](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1749)]
But isn't the annoying thing usually when you try to open the PR?

##### **Geohot** [[00:29:19](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1759)]
What do you mean?

##### **Chrism** [[00:29:21](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1761)]
If you were seeing that failing, then I, then I should definitely take a look at the, the, I, I, you, you've seen that fail.

##### **Chenyu** [[00:29:30](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1770)]
Yeah. So when I open the PR, I assume that's running on our...

##### **Chrism** [[00:29:35](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1775)]
Yes, that is running on our hardware.

##### **Chenyu** [[00:29:37](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1777)]
Yeah, sometimes it's a USB error. Sometimes it's a weird 'driver not found'. Okay. If you want reports, I can find a way to report this, because I feel it's quite frequent, but it's always gone after I retry.

##### **Chrism** [[00:29:57](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1797)]
Okay. I, I, yeah. I don't know. I'll look into this, seeing if there's a, so certainly I can report this on master because then we assume that all of them are all going to pass. Yeah. Yeah. Let's, let's,

##### **Geohot** [[00:30:11](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1811)]
Let's change it after this and let's take full responsibility for it.

##### **Chrism** [[00:30:14](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1814)]
Yeah.

##### **Chenyu** [[00:30:15](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1815)]
Cool. Sounds good. Okay. Moving on to HCQ2 and drivers.

##### **Nimlgen** [[00:30:24](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1824)]
Yeah, so I merged TCC for HCQ2. It should be default in CI. It's a lot faster, but it works on x86 only. It's really annoying, you basically cannot choose the output format on Macs. Because we expect ELF, and if you have an ARM host, like a Mac host, it will produce this Mach-O file. So yeah, but on Linux and x86 it should be fine, and the default one for CI.

##### **Geohot** [[00:31:08](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1868)]
For Mac, let's just do LLVM or whatever.

##### **Nimlgen** [[00:31:14](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1874)]
Also merged some VFIO stuff. Currently we can use VFIO to access the whole device, and that should be fine. The only missing part is I haven't added the udev rules to our image. Once that's added, we can completely drop all these requirements for Python admin capabilities.

##### **Geohot** [[00:31:48](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1908)]
Yeah, that's great. And are the udev rules egregious, or are they normal things that I can have on my computer?

##### **Nimlgen** [[00:31:58](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1918)]
You can add it to your computer. The problem is that something should change the permissions for the VFIO devices, because they require root as well by default.

##### **Geohot** [[00:32:22](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1942)]
Yeah, and that's what the udev rule is going to do.

##### **Nimlgen** [[00:32:25](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1945)]
Yeah.

##### **Geohot** [[00:32:26](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1946)]
Right. Yeah. So, um, I think that's, that's the best security boundary we can hope for.

##### **Nimlgen** [[00:32:43](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1963)]
I did some small HCQ2 changes, adopting EXTERN. So for the Kimi speed, I have the server alive now, so you can try it. The best prefill I get is about 600 tokens a second.

##### **Geohot** [[00:33:06](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1986)]
Okay.

##### **Nimlgen** [[00:33:07](https://www.youtube.com/watch?v=jPGI-sEdddk&t=1987)]
And that's mostly still compute-bound, so still looking into that. So the decode is about the same. It's like 35 tokens a second. Sometimes it's like 48, depending on the workload you run.

##### **Geohot** [[00:33:36](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2016)]
Um, yeah. [unclear] Hmm. That's pretty good. That's, that's pretty decent. Wow. I can't believe that's going off disk. Like, Kimi talks.

##### **Nimlgen** [[00:34:08](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2048)]
So, yeah, I focused mostly on Kimi 3.1, but I'll test GLM-5.3 as well. Maybe some other big models. Um, yeah.

##### **Geohot** [[00:34:24](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2064)]
GLM-5.3 is also interesting. We should just be able to use this pretty generically. I like how much you've been upstreaming into master.

##### **Nimlgen** [[00:34:33](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2073)]
The driver is upstream. I think the biggest difference is kernels, and maybe some...

##### **Geohot** [[00:34:49](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2089)]
Yeah. I'll take a look. Are you ready to start on the Chestnut project?

##### **Nimlgen** [[00:35:00](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2100)]
Yes. I think I'll, I'll start it this week.

##### **Geohot** [[00:35:04](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2104)]
Um,

##### **Nimlgen** [[00:35:05](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2105)]
Yeah.

##### **Geohot** [[00:35:07](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2107)]
Great. Yeah. Not TCC. You get SDCC. Yeah. But yeah, same basic idea. We should think about our minimal image with all the VM stuff. Right now our VM runs a Linux image, but we could imagine our VM instead running some hyper-small image that basically is just a tinygrad remote.

##### **Geohot** [[00:35:42](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2142)]
The thing to keep in mind for the goal of HCQ2 is: we can keep the Linux host. I don't mind the Linux host, or whatever the host is. Ideally, hopefully something that doesn't boot off a drive. But all these hosts spin up this super-small VM, and that VM opens a port. That port is accessible and allows remote tinygrad to drive all the GPUs.

##### **Chenyu** [[00:36:19](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2179)]
What's the Chestnut project?

##### **Geohot** [[00:36:29](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2189)]
Can you explain it?

##### **Nimlgen** [[00:36:31](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2191)]
Yeah. Basically, we wanted to move all the CPU host programs we currently run on the CPUs into the Chestnut and run them on it. On this 8051 CPU which is on the Chestnut. So yeah.

##### **Geohot** [[00:37:03](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2223)]
Yeah, and this should finally get rid of basically all the... There's a lot of latency in round-tripping to the host to talk over USB. But if you're running on the Chestnut processor, it should be a lot faster. We should be able to cut like five milliseconds off the latency of comma's models. And we also start to think about collectives, who sits and waits, how synchronization works, and all those things. To further genericize this idea of: okay, you have a communications pipe, you have some way to execute, and that's mostly it.

##### **Geohot** [[00:37:53](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2273)]
We also have Blasty's... I haven't looked into it too much except to check that it works. But we have code exec on the PSP of the 7900 XTXs. So you could imagine us also moving the stuff to the GPU itself. Yeah, that sounds cool.

##### **Nimlgen** [[00:38:26](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2306)]
The one which is posted in AMD hardware?

##### **Geohot** [[00:38:30](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2310)]
Yep. I mean, I think the Chestnut one's more practical. I just want to give a little vision. and I drew it on the board. The idea of the network-attached GPU. When you look at the AMD Helios rack, there's way too much stuff in there. There's CPUs in there, there's DPUs. I don't even really know what a DPU is. There's a lot of stuff. None of this makes any sense, right? They might say, 'Oh, you need CPUs in order to do the RL environments.' Yeah, that's fine. Why do the CPUs need to be anywhere near the GPUs? The bandwidth requirement for agents is dial-up.

##### **Geohot** [[00:39:21](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2361)]
Where I see everything going is pretty much network-attached GPUs. These GPUs already have some kind of processor on them which can handle any kind of HCQ-style stuff, can handle the out-of-band communications protocol. But mostly like, when I propose this to people, like George, you're an idiot. You can't just put a network port on a GPU because you need a low latency path. You need a low latency command path and then a high bandwidth path. I'm like, dude, you only need a low latency path if you are like driving it from a CPU, which you shouldn't be doing.

##### **Geohot** [[00:40:03](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2403)]
Like, we want to distribute. When we want to do a three day long training job, we want to distribute all the little programs and all the little pieces to all the little places. And then once the job's kicked off, there is only the high bandwidth communication between the GPUs and synchronization. So that's the big thing. Yeah. Just a vision of kind of where things are going. And why HCQ2 is so important.

##### **Chenyu** [[00:40:37](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2437)]
Do we have a Kimi branch and a pull request?

##### **Nimlgen** [[00:40:41](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2441)]
We have a pull request.

##### **Geohot** [[00:40:44](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2444)]
People are always asking about it. People don't believe it's real. People think that I made it up as a marketing.

##### **Qazalin** [[00:40:54](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2454)]
We can record.

##### **Geohot** [[00:40:56](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2456)]
Yeah. Cool. Yeah, that v1 link actually worked. I just talked to a Kimi that's running off disk. So if you buy a Kimi Box, you'll actually be able to run this branch. I used to say things like, 'You'll actually be able to run this branch,' when I knew that most people buying a box actually have no capability of doing that. But now you can just paste this into your agent and say, 'Run this branch,' and it'll do it.

##### **Geohot** [[00:41:28](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2488)]
Great.

##### **Chenyu** [[00:41:31](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2491)]
Deleting HCQ1.

##### **Geohot** [[00:41:34](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2494)]
Yeah, I'll delete it. Sounds good.

##### **Chenyu** [[00:41:41](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2501)]
OK, moving on to assembly.

##### **Qazalin** [[00:41:45](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2505)]
Yep. So I merged a lot of cleanups to x86. ETA end of this week, I'll switch x86 to the new CALL style. I already switched RDNA3 to the new CALL/ASM op. First thing, I have to fix x86's register dtypes, because x86 can go up to 512 bits, and currently we don't have 512-bit dtypes. So extend our dtypes to support it, because when I switch register to ALLOC, the subregister is a sub-dtype.

##### **Geohot** [[00:42:38](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2558)]
Adding dtypes?

##### **Qazalin** [[00:42:42](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2562)]
I think so. We need to add a dtype to represent it, because registers are a scalar, right? Shape empty tuple, to have a correct dtype.

##### **Geohot** [[00:43:00](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2580)]
Yeah, I mean, the idea would be that we have dtypes for, so I think our biggest dtype, do we have U128? So what's our biggest dtype right now?

##### **Qazalin** [[00:43:22](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2602)]
64.

##### **Geohot** [[00:43:24](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2604)]
Oh, we don't even have that. Yeah. We'll add, not the unsigned version, just the signed version. U128, U256, U512, and U1024. Okay.

##### **Chenyu** [[00:43:45](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2625)]
And those just act pretty much like storage formats, not ALU formats?

##### **Geohot** [[00:43:53](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2633)]
Yeah. I mean, we could add decomps to make them work as an ALU. No, wait, you should be able to use them as an ALU format too.

##### **Chenyu** [[00:44:07](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2647)]
And support it for all backends?

##### **Geohot** [[00:44:12](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2652)]
We should add decomps, right? Yeah. Yeah. Yeah. Yeah. I don't know. You can decide.

##### **Chenyu** [[00:44:22](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2662)]
I think it's fine. I mean, we have the long decomps, so...

##### **Geohot** [[00:44:28](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2668)]
Yeah, I mean, they shouldn't be like, they shouldn't need crazy bespoke decomps. It's just the same thing, but scaled a whole bunch.

##### **Chrism** [[00:44:38](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2678)]
Like, if you don't have long and you don't have 128, then it's going to be pretty ugly. But like, I don't know.

##### **Geohot** [[00:44:46](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2686)]
No, but what do you mean? It decomposes it all to 32s.

##### **Chrism** [[00:44:49](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2689)]
Well, yeah. But that code's going to look ugly.

##### **Geohot** [[00:44:53](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2693)]
OK. Is it going to be wrong?

##### **Chrism** [[00:44:56](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2696)]
No.

##### **Geohot** [[00:44:57](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2697)]
Yeah. So the alternative way to express this is like as like a shaped object. But that's just not the reality of the registers on these kind of machines.

##### **Chenyu** [[00:45:10](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2710)]
I think adding dtype is fine. Just making sure it's handled properly.

##### **Geohot** [[00:45:18](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2718)]
Yeah. We can start with them just being storage dtypes and not being numeric dtypes, and you have to bitcast. I think that's fine. Yeah. And like, there's not too many of these dtypes to add. They're not going to like massively overwhelm the system. They're just... Also, we don't have FP4 dtypes. We're looking at our dtypes now. Nope. No,

##### **Qazalin** [[00:45:46](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2746)]
We don't have FP4. The FP4 GEMMs, we can use [unclear] dtypes.

##### **Geohot** [[00:45:52](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2752)]
Yeah. Looks like we need FP4 dtypes though.

##### **Chenyu** [[00:45:59](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2759)]
Speaking of decomp, this is not related to assembly, but I just realized we don't have float64, double decomp. Do we want double decomp?

##### **Geohot** [[00:46:11](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2771)]
Yeah, probably.

##### **Chrism** [[00:46:14](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2774)]
I think we intentionally did not have it. But maybe we want it now.

##### **Chenyu** [[00:46:20](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2780)]
Yeah. I learned there are two algorithms to do this and neither looks good. So it will be more of a meme to add it. But I don't know who's going to maintain that.

##### **Chrism** [[00:46:35](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2795)]
This is why I did the denormals are zero thing is because it sucks to not do that.

##### **Geohot** [[00:46:41](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2801)]
Yeah. I don't know if double decomp is something we immediately need.

##### **Chenyu** [[00:46:49](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2809)]
Yeah. It's just slightly annoying if you write tests, you still need to remember adding is_dtype_supported just for double.

##### **Geohot** [[00:47:02](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2822)]
Anyway. Yeah, eventually these things will kind of become... Think of what an AVX instruction looks like and what dtypes are going into that AVX instruction and what you're getting. It's not really the shape that you can slice.

##### **Qazalin** [[00:47:18](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2838)]
Yeah. Do you think a VGPR is a (32,) with dtype uint32, or [unclear]?

##### **Geohot** [[00:47:29](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2849)]
Well, the VGPR, it's less clear because it supports indexed loads. But in something like the DSP, I think it's more obvious that it's...

##### **Qazalin** [[00:47:42](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2862)]
Well, the VGPR input to a WMMA is 1024.

##### **Geohot** [[00:47:54](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2874)]
Yeah. I don't know. Okay. Anyway. There's an argument to be made that it's actually not a dtype. Right. Because like, think about what the biggest, like, thing you're doing the operation itself. When you do add on a 1024-bit register, you're generally not doing the carry through the full 1024. So maybe it's not a new dtype. Maybe it is just shaped. And what's the dtype of that? Look, what instruction are you doing?

##### **Qazalin** [[00:48:39](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2919)]
Wait, no. No, it has to be one dtype, one register. Otherwise your UOp deduping breaks. You need one alloc to describe the register.

##### **Geohot** [[00:48:51](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2931)]
Yeah, then probably pick uint of the largest thing ever used. What's the biggest individual thing in an ALU op right now?

##### **Qazalin** [[00:49:01](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2941)]
Imagine you have an XMM and then you view it. The XMM is 128. Okay. In different instructions, you view it differently.

##### **Geohot** [[00:49:17](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2957)]
Yeah. You kind of view it differently.

##### **Qazalin** [[00:49:19](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2959)]
But the identity of the op shouldn't change.

##### **Geohot** [[00:49:22](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2962)]
Yeah, definitely. I agree that you have to pick one for the register. But I'm saying, what if you're only bitcasting to bigger shapes? What's the biggest dtype you can use that you'll never have to... For any of these instructions, what's the biggest thing you can do in an XMM?

##### **Qazalin** [[00:49:48](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2988)]
Biggest thing I can do. So if it's like 32, just pick that.

##### **Geohot** [[00:49:53](https://www.youtube.com/watch?v=jPGI-sEdddk&t=2993)]
Well, is it 32? When you add two XMMs together, what's the biggest chunk as an ALU, right? I think it's 32. It might be 64 if it can support two doubles. But either way, you maybe just pick that. Think about what the add actually means. Think about the difference between the add with the bitcast and the add without the bitcast. So yeah, I think it's 32. Do we have XMMs in x86? We do. Where are they? Regalloc. Here.

##### **Qazalin** [[00:50:28](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3028)]
It's in the constraint, alloc_vreg. It's the ALLOC.

##### **Geohot** [[00:50:37](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3037)]
XMM ops. VREG XMM. [unclear] Well, that's fine for the VREG, but where's the actual... What does this instruction do? Are these the instructions they're doing? Are they even doing math? What? I might be wrong on the 32. I mean, it looks like we're not handling any doubles. You see what I mean about how you don't actually need the dtype?

##### **Qazalin** [[00:51:30](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3090)]
Well, if you only use the, if the instruction only uses like 32 bits of that, just put your 32 on it.

##### **Geohot** [[00:51:38](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3098)]
Well, it uses more, but the question is like how much you can, how far the carry goes. Does that make sense?

##### **Chenyu** [[00:51:52](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3112)]
What's the smallest unit that still is an add?

##### **Geohot** [[00:51:56](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3116)]
Yeah. Yeah. Yeah. And we'd actually probably want to go with the biggest units.

##### **Chenyu** [[00:52:08](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3128)]
I mean, there's just one, basically what's the unit of that add if there's a carry, where does the carry stop?

##### **Geohot** [[00:52:16](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3136)]
Yeah. Yeah. Yeah. But I think it also depends on the instruction. I think the instructions support all the different types. I'm pretty sure there's XMM instructions that support viewing things as 8-bit, viewing things as 16-bit, viewing things as 32-bit.

##### **Chenyu** [[00:52:34](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3154)]
I think we should think more on this problem, and we should move on for the meeting.

##### **Geohot** [[00:52:43](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3163)]
Sounds good. Oh God, it's everything.

##### **Chenyu** [[00:52:50](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3170)]
I mean, 128 looks fine.

##### **Geohot** [[00:52:58](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3178)]
But then we have to add 128.

##### **Chenyu** [[00:53:00](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3180)]
Then we have 512. Do we support AVX?

##### **Geohot** [[00:53:04](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3184)]
Here are the AVX 256 types. I mean, maybe it should just be the biggest. I tend to think it's 32. Okay, anyway, think more about this. It's u32. All right, done. It's shaped u32, and we'll just go with that.

##### **Qazalin** [[00:53:32](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3212)]
We'll do it without [unclear].

##### **Geohot** [[00:53:34](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3214)]
If it's shaped u32, we can change it later. It's not that big a deal.

##### **Chenyu** [[00:53:38](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3218)]
OK. Moving on to EXTERN.

##### **Geohot** [[00:53:50](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3230)]
Okay. So I shipped two new functions in Tensor last night. CALLify was massively overkill. What CALLify was trying to do was pull everything out into PARAMs, and this required a whole lot of fancy analysis that had to be done before the cache.

##### **Geohot** [[00:54:19](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3259)]
So you have the schedule cache, and CALLify had to do this analysis beforehand, which made things slow. And the reason you can't just use PARAM in the first place without a CALL is you might be inside of a CALL. So I had a simple solution to this. I just added this new thing called Ops.EXTERN, which is basically the same thing as PARAM. PARAM has CALL scope and EXTERN has global scope. So it's just a globally scoped PARAM. When you have EXTERN with slot 3, no matter how many CALLs deep you are in that graph, it always means the exact same thing. Just think of EXTERN as globally scoped PARAM. I thought about calling it GPARAM, but I think EXTERN makes more sense.

##### **Geohot** [[00:55:04](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3304)]
So now we have a function called Tensor.export. It will convert all your buffers into EXTERNs. It will also convert your variables into EXTERNs, which gives you UIR that's really easy to export. So we have Tensor.export, which will give you this one UOp that can be exported to UIR. And then we have Tensor.run, which will run the compiled form of that UIR on that EXTERN-to-BUFFER mapping. So we can finally think about tinygrad as three stages. There's the frontend, there's the compiler, and there's the runtime. I moved all of schedule into codegen, because it really is just all codegen. Just think about taking the UOp graph in that you want to execute. I want to clean up the JIT too because of this. This is the same UIR that we can eventually embed in the safetensors when we want to say, 'This is actually how the thing runs.' The EXTERNs can be real EXTERNs, or the EXTERNs can maybe come from the safetensors file itself. We can figure out whatever API we want there.

##### **Geohot** [[00:56:13](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3373)]
But yeah, I mean, the idea basically is we can now export UIR that says, this is what you want to run. The compiler can spend a lot of time figuring out how to run it. And then the runtime. Ops.EXTERN is just Ops.PARAM, but with global scope. Does that make sense? Any questions about Ops.EXTERN? Cool. And the course is progressing. You can see where I'm at in studentgrad. I'll start on week seven, probably tomorrow.

##### **Chrism** [[00:57:02](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3422)]
Is from_blob...

##### **Geohot** [[00:57:03](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3423)]
Oh, sorry. Go ahead.

##### **Chrism** [[00:57:05](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3425)]
Is from_blob EXTERN?

##### **Geohot** [[00:57:09](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3429)]
I think so. from_blob just creates a BUFFER. So it's going to create a real BUFFER. And then BUFFERs are only converted to EXTERN when we want to pass it to the compiler. These are all just things I'm doing to keep the compiler pure. The compiler should never touch the runtime or the buffers or anything like that.

##### **Chrism** [[00:57:32](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3452)]
Okay.

##### **Geohot** [[00:57:37](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3457)]
Cool. So that is

##### **Chenyu** [[00:57:40](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3460)]
And that would just be the new JIT? JIT is basically just export all your things?

##### **Geohot** [[00:57:49](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3469)]
Yeah. You can imagine JIT being a UIR chunk, and every input to your JIT is an EXTERN. Notably, it's not a CALL. You don't have to do that. That just creates a lot more complexity. It's like function.py, which is kind of crap. We spent a lot of complexity trying to get it to be a CALL. But we don't actually have to make it a CALL as long as EXTERN has global scope.

##### **Chenyu** [[00:58:24](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3504)]
I see.

##### **Geohot** [[00:58:27](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3507)]
From a JIT's perspective, EXTERN is literally just anything that does not exist inside the JIT function, anything that comes from the outside world. Then we can split our EXTERNs into explicit EXTERNs and implicit EXTERNs. But they're still both EXTERNs. Just like PARAM, but with global scope. Two PARAMs in the same graph may refer to different things. They can refer to different invocations of a CALL. They can be in different CALLs. But two EXTERNs, if they have the same slot number, are always the same.

##### **Chenyu** [[00:59:13](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3553)]
Okay. Sounds good.

##### **Geohot** [[00:59:21](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3561)]
I'll push more of this stuff. Also, you're going to be able to do python -m tinygrad compile and pass in a UIR file. It's going to compile that UIR file as far as we can possibly go. So we've finally separated the compilation piece from the frontend piece. And then we're going to do the same thing on the runtime piece.

##### **Qazalin** [[00:59:39](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3579)]
Does EXTERN have a dtype?

##### **Geohot** [[00:59:44](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3584)]
Yep. Identical to PARAM in every way.

##### **Qazalin** [[00:59:45](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3585)]
But the slot thing, as you mentioned, the slot rule.

##### **Geohot** [[00:59:49](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3589)]
Yeah. So if you ever make two EXTERNs that both have slot 3 and have different dtypes, that's an error. That's an invalid graph. We can check it. Sounds good. Okay. So,

##### **Chenyu** [[01:00:07](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3607)]
Anything else?

##### **Geohot** [[01:00:09](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3609)]
Nope.

##### **Chenyu** [[01:00:11](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3611)]
Not big. I'll be fast. Moving on. So I just continued fixing a bunch of AFTER/effect stuff. You can see my change. I think we briefly discussed this in Hong Kong, but a new idea for cleaning this up is: behavior shouldn't be different based on how good our rewrite rules or symbolic engines are. I'm basically fuzzing these ideas to see where we do things differently.

##### **Chenyu** [[01:00:50](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3650)]
Specifically, I want to know how people feel about this. For now, we have axis types for RANGE, and the default is WEAK. WEAK means you can parallelize each individual thing. So WEAK can later become GLOBAL, become LOCAL, become UPCAST, and things like that. We have another axis type, LOOP, which means sequential. It needs to be sequential to be correct. Basically it guarantees the execution order. For now our default is WEAK, which means when a user uses this API and actually means LOOP, it can be wrong. If something should be LOOP and it's WEAK, it will be wrong. And I think that's better than defaulting everything to LOOP.

##### **Geohot** [[01:01:58](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3718)]
You think it's better to default to weak or better to default to loop?

##### **Chenyu** [[01:02:03](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3723)]
Not clear to me. Because having silent error is bad. But the other way is you might have like regression. And in any case, the analysis to know if it's safe to make it parallel is pretty hard.

##### **Geohot** [[01:02:24](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3744)]
Yeah. I mean, LOOP also means that it's explicitly serial and not upcasted. So it's not like, 'Oh, I'm going to upcast it.' I don't know. I'm open to either.

##### **Chenyu** [[01:02:43](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3763)]
Yeah. So I made the change already. You can see my draft. It's not a very big change. But this really ties to people who write more custom kernel. Are people really concerned with things like this? Yeah. Because I also don't know how well the agents are dealing with this. Because these race conditions are like, they'll probably be right most of the time, which makes it even more annoying.

##### **Geohot** [[01:03:18](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3798)]
Yeah. I generally agree that it should be loop. Because that is kind of the, since it's called range, that is kind of the default should be loop. Yeah. For the kernels that are written by the agents, all the axes are explicitly specified.

##### **Chenyu** [[01:03:39](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3819)]
I see. Maybe that's a good start. Okay, sounds good. If there's no objection to this, I would think more about probably leaning into defaulting to LOOP. Internally, every place that can be WEAK because we do some optimization, and the internal things we insert, I explicitly annotate those to make sure it's not regressing anything. It's just the user code that needs to be changed or updated.

##### **Geohot** [[01:04:18](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3858)]
Yeah. I'm supportive of this. I think it's just a question of whether your WEAK is before the optimizer. But one of the really important properties of tinygrad's compiler is that it's reentrant. So if you have something, you optimize it, and then you put it through the optimizer again, it doesn't change the second time.

##### **Chenyu** [[01:04:44](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3884)]
Yep.

##### **Geohot** [[01:04:45](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3885)]
Okay. But yeah, no. So I think like, the question is, like, do you want to like leave that unoptimized or like optimize it, and like what do you want the default to be? I would suspect that you want the default to be loop. Especially because the other thing about it being WEAK is, if you specify one of your axes as GLOBAL, the optimizer may add a second GLOBAL axis, and that might not be what you want if you leave it WEAK.

##### **Chrism** [[01:05:16](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3916)]
Yeah.

##### **Geohot** [[01:05:20](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3920)]
I don't know if in practice, but yeah.

##### **Chenyu** [[01:05:23](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3923)]
I think this follows our principle that the default is always correct. If you know more details about this and want the most specific version that's fast, you can still do it.

##### **Geohot** [[01:05:39](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3939)]
Cool.

##### **Chenyu** [[01:05:41](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3941)]
Yeah, so... About matching studentgrad, currently it boils down to two issues. One is still some AFTER/effects thing that I'm cleaning up. Another is I saw you added a bunch of really big tests. If you run tinygrad now, it would just hang. I'm working on root-causing those and seeing what can be done.

##### **Chenyu** [[01:06:10](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3970)]
It pretty much boils down to the AFTER/effect thing, the complexity thing, and some of the numerical things where we just decide to be different. That's probably fine.

##### **Geohot** [[01:06:24](https://www.youtube.com/watch?v=jPGI-sEdddk&t=3984)]
Yeah, the numerics are even going to get dropped in studentgrad soon. Some of those tests that I've added with the reshape/permute things are brutal. There's not a good way to optimize them. They're just speed tests. But I don't know if you've actually run the studentgrad test suite. The entire studentgrad test suite runs in like three seconds.

##### **Chenyu** [[01:06:49](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4009)]
No, I only run the tinygrad version.

##### **Geohot** [[01:06:54](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4014)]
Oh, yeah, studentgrad is extremely fast.

##### **Chenyu** [[01:06:59](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4019)]
It's just a few hundred lines, 200, 300, something like that.

##### **Geohot** [[01:07:04](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4024)]
Yeah, but the output in symbolic code is not very good. Cool.

##### **Chenyu** [[01:07:08](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4028)]
Okay. That's pretty much my stuff, so I will continue on this. Also, quickly discuss: what do we do about public pull requests now? It has a big queue.

##### **Geohot** [[01:07:28](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4048)]
Some of them were good and I merged them.

##### **Chenyu** [[01:07:32](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4052)]
Yeah, I also merged some, and the things from Teddy, it's okay.

##### **Geohot** [[01:07:37](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4057)]
There's kind of too many pull requests.

##### **Chenyu** [[01:07:40](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4060)]
Teddy is kind of half-half.

##### **Geohot** [[01:07:44](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4064)]
Half-half what?

##### **Chenyu** [[01:07:46](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4066)]
Half kind of good and interesting to merge, the other half is like, why?

##### **Qazalin** [[01:07:54](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4074)]
You saw his emulator PR? He's definitely a [unclear].

##### **Chenyu** [[01:08:01](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4081)]
Yeah, I mean, that was very clear from the start, and still some of the things are good.

##### **Qazalin** [[01:08:10](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4090)]
Yeah, it's good to have people.

##### **Geohot** [[01:08:12](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4092)]
But some of it is not. Okay.

##### **Chenyu** [[01:08:21](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4101)]
Anyway, I will review these. So anything that is not reviewed is probably the worst half.

##### **Geohot** [[01:08:29](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4109)]
Unless you are confident it is, close it. Putting up a pull request means you think this is worth a person's time. Unless you are highly confident that it is, close it.

##### **Chenyu** [[01:08:45](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4125)]
Yeah.

##### **Geohot** [[01:08:51](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4131)]
Okay.

##### **Chenyu** [[01:08:55](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4135)]
Anything to add for bounties? Are bounties still running?

##### **Geohot** [[01:09:02](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4142)]
Not really. Bounties are kind of over with AI. Too many pull requests already. They're still up there. Look, if someone does them and does an incredible job. But I don't want slop that's like, 'Oh, it technically meets the definition.' I'm like, dude, I'm not going to pay it. I think the caveats on the bounties are pretty clear. Yeah. Okay.

##### **Chenyu** [[01:09:29](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4169)]
Okay, I would find some time to go through these and probably close some of the old ones that no one is going to merge.

##### **Geohot** [[01:09:43](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4183)]
Yeah. I don't know. I also just paste them in Astra and say, 'Hey, is this good?' We could just have Astra go through all 60.

##### **Chenyu** [[01:09:58](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4198)]
Well, the issue is, for these, other than my personal review, I also have three different AIs reviewing those. It's not really about AI reviewing those. The issue is always I feel like there's a better way to do this. If I start to invest time, then why do I need this to start with? I already have a bug list that's probably 100 different bugs.

##### **Geohot** [[01:10:25](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4225)]
Yeah, it may be worth writing some automation. In my prompt, I don't just say, 'Review this code.' I have a prompt that I paste in that says, 'Is this code really worthwhile to merge for the tinygrad project?'

##### **Chenyu** [[01:10:42](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4242)]
Yeah, I think a good bar is really I saw you ask this in some PR like, is it really an issue people hit which we might prioritize more or if you just run it through AI and ask for bug, we're going to have enough of those.

##### **Geohot** [[01:10:57](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4257)]
Yeah, exactly.

##### **Chenyu** [[01:11:00](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4260)]
Okay, cool.

##### **Geohot** [[01:11:02](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4262)]
We can ask AI what they did. If the AI thinks they just ran it through AI and looked for bugs, you can just close it.

##### **Chenyu** [[01:11:10](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4270)]
Yeah, that's a lot of these. Okay. Sounds good. I'll probably just close some of the really old ones. We still have ones from like July.

##### **Geohot** [[01:11:22](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4282)]
Yeah. The oldest one is still the DSP one.

##### **Chenyu** [[01:11:29](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4289)]
That one is paid, right? Can we close it?

##### **Geohot** [[01:11:32](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4292)]
No, I want to I want to bring the DSP back. I think yeah, we can bring it back.

##### **Qazalin** [[01:11:37](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4297)]
Yeah, DSP is the future.

##### **Chenyu** [[01:11:40](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4300)]
Wait, DSP is removed.

##### **Geohot** [[01:11:43](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4303)]
We're gonna bring it. Oh, it never actually got merged. It was never upstream.

##### **Chenyu** [[01:11:48](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4308)]
So we have DSP, it's just not fast.

##### **Wozeparrot** [[01:11:51](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4311)]
The backend exists, it's not fast.

##### **Geohot** [[01:11:53](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4313)]
Oh, the back end exists. Yeah, it's not fast. And and yeah. And maybe we do want that u1024.

##### **Qazalin** [[01:12:01](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4321)]
We do want it.

##### **Geohot** [[01:12:06](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4326)]
Anyway, sounds good.

##### **Chenyu** [[01:12:07](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4327)]
Yeah, okay.

##### **Geohot** [[01:12:08](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4328)]
We'll have the dtypes. You can use them or not.

##### **Chenyu** [[01:12:13](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4333)]
Sure. If you handle all the dtype and its promotion rules, fine.

##### **Geohot** [[01:12:19](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4339)]
Just put them out of the promotion tree. It can't be promoted.

##### **Chenyu** [[01:12:24](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4344)]
That works too. But then you need to make sure nothing will promote into that as well. Something like that.

##### **Geohot** [[01:12:31](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4351)]
Yeah, they don't exist in the promotion tree. They can't promote. They're just like blob dtypes.

##### **Chenyu** [[01:12:40](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4360)]
Sounds good. So looking forward to the service launch. I think that's it for this week. Thank you, everyone. See you next week. Oh, sorry.

##### **Chrism** [[01:12:52](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4372)]
One thing is that, B1TG, can you... I just noticed that CI is deadlocked. It's because all of the VM hosts are fully occupied and R1 needs to reboot because it's soft-bricked.

##### **Geohot** [[01:13:07](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4387)]
I'll kill one of mine.

##### **Chrism** [[01:13:10](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4390)]
No, or that. But if, B1TG, you kill your VM that has a single GPU, then it will allow R1 to reboot and fix it.

##### **Geohot** [[01:13:19](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4399)]
Let me just kill one of mine. And then also let's add TR7 and... Yeah, yeah. Sounds good.

##### **Chenyu** [[01:13:37](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4417)]
Okay, that's it for the meeting. Thank you, everyone. See you next week. Bye-bye.

##### **Geohot** [[01:13:42](https://www.youtube.com/watch?v=jPGI-sEdddk&t=4422)]
Bye.
