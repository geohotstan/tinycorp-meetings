# 2025-09-22 Meeting

### Meeting Agenda

**Time:** 9am Monday San Diego time
- company update
- RANGEIFY! store / assign / group reduce / disk / jit / const folding / buf limit / llm / openpilot children not making progress / image
- other bounties

### Audio

[Youtube Link](https://www.youtube.com/watch?v=IuaE1LK9_SQ)

### Highlights

- **[Meeting Time Change](#chenyu-000009)**: Starting next Monday, the meeting will be pushed back by three hours to accommodate the team's time in Asia; announcement to be posted in the channel and event updated.
- **[Company Update](#chenyu-000042)**: Sold a few more Tiny Boxes; no major updates on provisioning machines, which have been depleted.
- **[Rangeify Overview](#chenyu-000121)**: Rangeify is the new scheduler for tinygrad, aimed at fixing issues to make it the default; enables advanced features like fusion, local buffers, flash attention; focus on resolving store/assign, group reduce, disk, JIT, const folding, buffer limits, LLM, openpilot, and image issues.
- **[Store/Assign Issues](#chenyu-000222)**: Current state involves incomplete handling of buffers, views, and constants in the graph; copy operations need optimization for expansions; Qazalin working on multi-device copies and fixing pointer swaps in tensors post-realize, addressing bugs from old scheduler.
- **[Group Reduce Problems](#chenyu-000617)**: Fails in linearizer for nested reduces; issue with if statements for shared memory reduction across thread blocks; discussion on removing unnecessary ifs since all threads can perform the work safely, avoiding write conflicts on AMD; plan to add custom error for unsupported cases before merging as default.
- **[Disk Handling](#chenyu-001004)**: Fixed as part of copy improvements; old issue with copying disk-opened NumPy arrays resolved by avoiding invalid kernel runs on disk; remaining cleanup involves using shape trackers instead of hacks, no Rangeify-specific issues left.
- **[JIT Fixes](#chenyu-001202)**: Symbolic JIT fixed by Sieds; copy-related JIT issues resolved; some shape update problems persist but tests pass; input realization now works correctly.
- **[GPT-2 Output Issues](#qazalin-001316)**: GPT-2 produces wrong output in Rangeify; potentially linked to group reduce; plan to disable group reduce temporarily with an error to ensure correctness, then investigate; also fusing RoPE embeddings creates large slow buffers.
- **[Fusion and Performance](#chenyu-001423)**: Rangeify fuses aggressively, leading to slowdowns like in GPT-2; prioritize correctness first (fix errors), then optimize cost function for fusion decisions post-correctness.
- **[Rewrite Rules and Index Dtype](#qazalin-001705)**: Issues with arbitrary casts breaking index dtype, causing ALU errors; related to image tests; plan to delete problematic section zero rewrites (e.g., tags disappearing, reduce folding); kernel counts improved with better fusion.
- **[Buffer Limit](#chenyu-001739)**: Not yet implemented, causing test failures on Metal GPU; Nimlgen to investigate.
- **[Openpilot Children Not Progressing](#qazalin-001910)**: Related to uncached map pad calls hitting 10,000 iteration limit; symbolic shapes cause deep indexing slowdowns; not infinite recursion but long single calls; need better caching for symbolic map pad and examples to debug.
- **[Image Issues](#chenyu-002230)**: Persistent index dtype problems from casts; isolated feature, easier to debug after other fixes.
- **[Stats Database Update](#wozeparrot-002512)**: InfluxDB corrupted after power outage; new data collection working, historic data recovering; issue with versions >3.0 hanging on start; limitation fetching data past 12 days; temporary setup, migration to alternative database planned.
- **[Stable Diffusion Bounty](#chenyu-002857)**: Training ongoing with last checkpoint eval in ~1 hour; reduce beam search to drop end-to-end time to 24 hours; issues with driver faults on beam=1 and memory leaks; focus on pinning crashing ASTs/optimizations; trade-offs in beam parameters for search speed vs. kernel performance; 10x utilization gap partly from power limiting.
- **[Core Tinygrad Changes](#chenyu-003511)**: For crashing kernels and mismatches (e.g., dtype upcast/downcast hacks), propose inclusion if aligned with Torch/Dex behaviors; custom implementations acceptable otherwise.
- **[RetinaNet Bounty](#flata-003632)**: Eval script issues with JIT on mask_select due to internal realize/dot_item calls; device mismatches in multi-GPU; NumPy version faster; exploring batching improvements for prediction loops/splits; plan to fix device specs and remove realizes, collaborate on mask_select implementation.
- **[FP8 Bounty](#b1tg-004003)**: B1tg completing FP8 work; needs access to red machine for final testing; access to be granted on green machine or equivalent.

### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=0)]
George is on break. He won't be joining today. We can get started.

##### **Chenyu** [[00:00:09](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=9)]
So first thing starting from next Monday, we will push this meeting back by three hours because we will be in Asia. That time works better. I will put an announcement in this channel and update the event.

##### **Chenyu** [[00:00:30](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=30)]
Speaking of the event, start event.

##### **Chenyu** [[00:00:35](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=35)]
Okay.

##### **Chenyu** [[00:00:38](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=38)]
More. House for company update.

##### **Chenyu** [[00:00:42](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=42)]
We usually talk about how many box we sell. I think we sold a few more. That's about it.

##### **Chenyu** [[00:00:50](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=50)]
I don't know if it was perhaps any update for the provision machine or anything regarding provisioning. 

##### **Wozeparrot** [[00:01:01](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=50)]
Not really. The machines are gone. Oh, good.

##### **Chenyu** [[00:01:09](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=69)]
Oh, okay.

##### **Chenyu** [[00:01:11](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=71)]
Is that good? I don't know. And Let's the company update.

##### **Chenyu** [[00:01:21](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=81)]
And next, basically the main point and what everyone has been doing for the past week is rangeify. For the people who want to get the So in this meeting rangeify is the new, I guess, paradise shift for tiny grads that we are trying to fix every box in it so we can make rangeify the default. rangeify leads to all the advanced fusion local buffer support flash attention and friends. So we really want to get this working and basically pass everything and that we can remove start to remove a lot. So I just list some I guess issue or the things that I can think of here and we can go through that. See if people have ideas for what it is.

##### **Chenyu** [[00:02:13](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=133)]
And we can start with store and assign. Yes, also copy.

##### **Chenyu** [[00:02:22](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=142)]
Maybe I also had some ideas for what's the current state of this. Are things broken? Are there like acts?

##### **Chenyu** [[00:02:28](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=148)]
I would need to remove first or any other. I think so. Okay. Copy should be thanks.

##### **Qazalin** [[00:02:40](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=160)]
If there any, you know, Yeah, I'm working on multi right now. The copy. It wasn't just like realizing things correctly. So that was also the issue with the jets.

##### **Chenyu** [[00:02:59](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=179)]
Maybe we just briefly goes through like what was the issue? I think we can break down issues in terms of there are some pack and or things are not complete and or there's just something that we don't understand.

##### **Qazalin** [[00:03:17](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=197)]
It's mostly that things are incomplete. So in the original range of high design, it only put back offers into the graph. That's not always true. You can see. Like sometimes you need to put constants back into the graph. Sometimes you need to put a view of a buffer back into the graph. It's different from the original structure. So for example, you can imagine I have a buffer and then I expanded and then I copy it. It's wasteful to do the expand before the copy. What you want to do is you want to copy and then do the expand on the other device. So that I can range of it and have a way to specify that or expresses. I remove the hacks that deal those with this in the wrong way. It's basically just a question of because you opt are currently immutable and they should be immutable. You have to update the pointer of the tensor. So after a present will get the a plus B and then you call realize on that. I expect that that tensor would be. Become a buffer. The way we currently deal with this is we have a pointer of a you up in the tensor and then we just swap up the ads with the buffer. So this was buggy in the old scheduler. It's showing cracks in the new branch of my stuff. Which is just like a sign of this an inherently hard problem. But yeah, I'm going through the excess. Currently, I'm working on. Yeah.

##### **Chenyu** [[00:05:05](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=305)]
Sorry back to the start. I think there are still issues for an external test. I do something. There's like a permutator sign something still wrong.

##### **Qazalin** [[00:05:18](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=318)]
Those are mostly asserts. Like if you have a cycle, we used to a shirt that you had a cycle now, which is so I think for now.

##### **Chenyu** [[00:05:28](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=328)]
It doesn't have assert by the output is wrong.

##### **Qazalin** [[00:05:32](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=332)]
It gives the wrong answer, which is shouldn't. The path forward for a sign is either fix it and never assert cycles. Or assert cycles and the old scheduler. So you can be actually like in range of is nice because you can insert buffers right before to cycle would happen.

##### **Chenyu** [[00:05:57](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=357)]
Okay. I think generally I go through the like the fail test or the things that still fail was rangeify is the things that wrong. But I'll put is incorrect. That's very bothersome.

##### **Wozeparrot** [[00:06:13](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=373)]
And I think that's yeah.

##### **Chenyu** [[00:06:17](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=377)]
I think the next one is reproduce and I think it reproduces really suffer from this. So. See it's fixed. Some of the linearizer value or to that case, but I think group reduce is still wrong.

##### **Sieds Lykles** [[00:06:39](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=399)]
Yeah. So it's not going in linearizer error anymore, but we're not properly putting the like the problem that the case is causing a problem is if you have a. So it's not going in linearizer error anymore, but we're not properly putting the like the problem that the case is causing a problem is if you have a. Group reduce inside of another range like inside another reduce. So. What happens is after the end of the group produce. You have a if statement. So that the shared memories reduced. By only one thread. And then once you're outside of. The range that's surrounding the group produce. You need to be inside an if statement again because you've closed the. Like local range. It's a bit tricky. I see.

##### **Chenyu** [[00:07:48](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=468)]
So I said I'm in my.

##### **Chenyu** [[00:07:52](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=472)]
It's true. Let's see if we can.

##### **Sieds Lykles** [[00:07:55](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=475)]
Sorry, go ahead. I was kind of thinking that. We don't. I'm not sure we actually need the if statement. Because of all the threads. Just do the same.

##### **Chenyu** [[00:08:09](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=489)]
Oh, yeah. Well, that's another thing that I think we discussed like a long, long time back. It's like there's nothing wrong if all the threads are doing the. Work. Anyway. Yeah. It's not like you are. You are. You will get faster. I think.

##### **Sieds Lykles** [[00:08:26](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=506)]
Because now the problem is that some of the threads are. Doing some and some of the threads are not doing a song. And then if they all try and write to the same address then. On Nvidia right now, it's correct because it writes the first element, which is the one that did the sum. But on the AMD.

##### **Chenyu** [[00:08:51](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=531)]
I don't think that we can rely on anyway. No.

##### **Sieds Lykles** [[00:08:55](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=535)]
No. Okay.

##### **Chenyu** [[00:08:56](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=536)]
So I think I think think see if you can add an arrow in this case. I'm custom arrow. I think the. Before before like merging rangeify as a default. I think the order is we definitely want to get rid of all the island. The wrong outputs by replacing that by some custom arrow. That's fine. And we can fix that. At least we understand that under this condition. It would. It's an arrow that we throw some arrow that we can make her decide. Maybe maybe there's some issue with the spec or something's not complete or we need to render render to like render differently. Like without like removing the if or something like that. But I think the good first step is to see if we can like always raise an issue saying this is not supported.

##### **Flata** [[00:09:57](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=597)]
Hey.

##### **Chenyu** [[00:10:01](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=601)]
Isk.

##### **Chenyu** [[00:10:04](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=604)]
If you disk was fixed as part of a copy. I think there was an old issue that if you open something on a disk, then you will try to code that numpy. It will fail because it. It will say some kernel needs to be wrong on disk, but this doesn't have. The ability to wrong a kernel like that. I think it's mostly gone.

##### **Qazalin** [[00:10:28](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=628)]
This because it blocks my copy stuff. Yeah. The fix I have is basically exactly what they schedule their old schedule. That was so it was wants to look into the disk stuff. There are still so there's a to do in range of fight out pi for this. It's using shape tracker. You have the tape tracker. It shouldn't it should just use the shrink. And there are still pending stuff in tensor. As our disk hacks, but none of them are range of five related. Most of those are just things that have existed. Wonderful.

##### **Chenyu** [[00:11:09](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=669)]
Was part of the data. Change to check disk.

##### **Wozeparrot** [[00:11:15](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=675)]
Yeah, I looked at this briefly. The one issue I did find was that it was trying to run kernels on this.

##### **Chenyu** [[00:11:23](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=683)]
Yeah, that was the issue. And I think that's fixed. If it's just a copy like copy the underlying buffer to non-pipe offer.

##### **Flata** [[00:11:32](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=692)]
Yeah.

##### **Chenyu** [[00:11:36](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=696)]
Okay. So I think we're remaining this one is probably just some like clean up. That should be done.

##### **Qazalin** [[00:11:46](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=706)]
Yeah, I think just remove the ST call like use proper shrink and stuff. I didn't put much time into this. I think it's just a little bit of a I can't think or ideas there.

##### **Wozeparrot** [[00:11:57](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=717)]
Yeah.

##### **Flata** [[00:11:59](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=719)]
Okay.

##### **Chenyu** [[00:12:02](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=722)]
I think you probably also mentioned something was fixed or I think in the emerging also did some fix on test. Good. Well, the symbolic jet is fixed by seeds. Mostly then the jitters of the copy legit. It's also fixed. I mean, there are still some. Some issues that JIT will return you the wrong shape because it doesn't update the shape force involved. Let's handle the same behavior.

##### **Chenyu** [[00:12:39](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=759)]
We have passed.

##### **Chenyu** [[00:12:48](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=768)]
Yeah, so I see test JIT is in range of I test. I think are we all good there?

##### **Nimlgen** [[00:12:58](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=778)]
Yeah, actually the JIT problems were related to is realized as well. So the same issue is copious.

##### **Qazalin** [[00:13:07](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=787)]
Is it still not realizing inputs? I thought I'll face.

##### **Nimlgen** [[00:13:11](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=791)]
Oh, no, no, it's it's good. Now. It's good. Now.

##### **Qazalin** [[00:13:16](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=796)]
There is a problem with GPT-2 is producing the wrong output is anyone looking into that?

##### **Nimlgen** [[00:13:22](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=802)]
I'm going to do that, but maybe it's because of the group reduce. If we have any problems with it. Might happen with GPT-2 as well.

##### **Chenyu** [[00:13:37](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=817)]
Yeah, let's let's see if we can quickly raise some arrow for group reduce then we can like don't do group reduce or rangeify as a next step. After we understand the issue and the triggering criteria, we can kind of. Disable that first so that at least the output is correct. I think another thing related to or GPT-2 is I think it's fusing the rope bedding so that it has a like a very big buffer and very slow.

##### **Sieds Lykles** [[00:14:16](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=856)]
I think in general the range of fire is flu using like a lot.

##### **Chenyu** [[00:14:23](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=863)]
So I think if the issue is the cost function to decide like what to fuse and what not to fuse then we can decide here. I think for. Hope specifically. I don't know. We'll get there. I think I think let's fix this prioritize the correctness first and like fix the issue. If it's not just optimization. For. Speed. And not a correctness issue. We can wait for I guess. That's that's the last thing before we make this the default. So we fix the arrow first. We make them. We make sure we understand the behavior and we see we fix all the correctness issue then see like. After that to get a good default, we need to make sure its performance then there we can optimize the cost function as. I think. So on the right side we can put that here for� rented a lot of testing and the same means we can control the prevents this one to the check dev. Will be heard a little bit IMG sense to me. Meet us in the next evaluation on what we're doing with constituting or maybe anything dancing in there. generally a problem with index. I think some rewriting rules, we just cast things arbitrarily, and if something should be in a dtype index, but we cast it to something that is not dtype index, then the whole thing becomes not dtype index, and later you have an issue with some ALU. So I don't really understand this, but I think it might be related to image. And I also think some of the cast thing, I don't understand the scope of this very well, but we have some tests that the error is less than, it's not defined between invalid and

##### **Flata** [[00:16:38](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=998)]
thing.

##### **Chenyu** [[00:16:40](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1000)]
You should know that. I will probably continue looking. I think Quazling also expressed that we want to delete everything in the section zero rewrite. Some of it was causing problems.

##### **Qazalin** [[00:17:05](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1025)]
We do. The tags are so hard to deal with. The tags just disappear from the graph and then nothing realizes. There are some good stuff in there. I know that reduce folding is this in there. I think that should remove that too.

##### **Chenyu** [[00:17:30](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1050)]
Yeah, okay. I will see what I can do with const folding and other folding stuff. In general, I think the kernel counts errors to be on the good side. Something that was not handled before now is handled and properly fused. The remaining, some of the remaining ones for model, I think I would change that at the very end. Again, that's not for, that's more of a what's the evil cost function for when to fuse. And I think as long as it's correct, we can always like test those later. So that I worry less about. Okay. Next is buffer limit. I believe we don't currently implement this. So that for like metal GPU, some tests fail because of that.

##### **Nimlgen** [[00:18:27](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1107)]
Yeah, probably I can take a look into this.

##### **Chenyu** [[00:18:31](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1111)]
Okay.

##### **Chenyu** [[00:18:37](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1117)]
Sounds good. Okay. Oh, we already discussed. Let's disable group reduce. I think this is the issue is it's fusing too much stuff and it's slow. So as long as the output is correct, it's correct on the rangeify equals to one PR is just like 10 minutes to run. So I think that we can wait. The open pilot, oh, children not making progress. This I don't know if anyone has.

##### **Qazalin** [[00:19:10](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1150)]
I believe that's related to pad. This stuff was the case for vinaigrette. Map pad isn't cached right now. So it keeps calling it. And it never actually like resolves. At least like it hits the 10,000 limits of the. rangeify. I'm sure it will resolve at some point in some distant future. We should catch that thing. And we.

##### **Sieds Lykles** [[00:19:47](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1187)]
Right. I mean, the cash. I think we talked about this is for symbolic, right?

##### **Chenyu** [[00:19:52](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1192)]
Yeah.

##### **Sieds Lykles** [[00:19:54](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1194)]
But it's for that effect. The children not making progress.

##### **Qazalin** [[00:20:03](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1203)]
So because like the threshold is that if you. If you have a child. Come back with an index with two children. For example, and one child hasn't yet finished doing the indexing. For 10,000 times. You'll end up getting an error. It's just as for the cough from. In a garage. Where map pad would keep on calling itself. Not resolving in the end.

##### **Sieds Lykles** [[00:20:37](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1237)]
But it's not. Is not that like actually. Calling itself.

##### **Qazalin** [[00:20:44](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1244)]
I don't know if it's calling itself, but they get the. Graphy rights. Loop level. Something keeps calling map pad. Do you think that's not the problem here? So I think that should be. Hit. Every time I control C it's hanging in map pad.

##### **Sieds Lykles** [[00:21:11](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1271)]
We. Yeah, but I, like, I mean, the times I looked. At it, it was just one single really long map pad call. And that's because. I mean, I, I can't, I did like a, I try to cash. And it's a bit faster, but it's still. Like the U of M valid. It's just pretty. Slow. If you have a very big valid. With a lot of expressions. And very deep. Index. I mean. Like a single call to map pad should. Pretty much entirely simplify the index. So I don't, I don't think. Map. Pad has been called. Many times. Like it might take a long time in map pad. But I don't understand how that would. Pause. Like. Children not making progress.

##### **Chenyu** [[00:22:30](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1350)]
Okay. I mean. I don't think we have. A. Answer. No. Let's find. Let's see if we can find other. Other examples. That. Is causing this issue. And. What can we do next? Okay. So image we discussed before. There was. Some. Index issue. I don't quite understand. But again, images quite isolated as a feature. So maybe if we fix. Other issues. It would become much. Easier. To understand what was left.

##### **Chenyu** [[00:23:07](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1387)]
Okay.

##### **Chenyu** [[00:23:19](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1399)]
Is there anything I missed? That the issues you are aware. But. I didn't. Listen here.

##### **Chenyu** [[00:23:33](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1413)]
Okay. So.

##### **Chenyu** [[00:24:01](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1441)]
For things. That we did fix. I think most of the annex stuff is. Fixed. The high level tensor stuff is. Looks good. We added a lot more tests. Also. I just added. The. Mac OS. For. Metal as well. It's quite annoying. That sometimes. It works for. Especially. Open COS. I don't know why it's different. Sometimes. Open. Open COS. Fails in one of the. Metal and Linux version. I just added. Okay. So. First. Of issues. Inter d. Up to.

##### **Chenyu** [[00:24:50](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1490)]
propor.

##### **Chenyu** [[00:24:51](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1491)]
I just mean.

##### **Chenyu** [[00:24:54](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1494)]
Hmm.

##### **Chenyu** [[00:24:56](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1496)]
Alright, then.

##### **Chenyu** [[00:24:57](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1497)]
So.

##### **Chenyu** [[00:25:00](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1500)]
I will. Anything that's. Different. To.

##### **Wozeparrot** [[00:25:12](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1512)]
We can give a little stats. Oh yeah what's the.. is it working now? Oh it's working now okay. It's working but we don't have historic data. No.. It will be back, historic data will be back. But so as of right now the database that we use for stats is influxdb.

##### **Nimlgen** [[00:25:42](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1542)]
Okay.

##### **Wozeparrot** [[00:25:45](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1545)]
The after the power outage the database corrupted.

##### **Chenyu** [[00:25:52](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1552)]
Okay.

##### **Wozeparrot** [[00:25:54](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1554)]
Great but that was a pretty easy fix and I also thought I'll do a.. I'll do a minor version bump.

##### **Wozeparrot** [[00:26:04](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1564)]
Or..

##### **Wozeparrot** [[00:26:04](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1564)]
And then the problem is for the database. Okay. And then there's an open GitHub issue on influx right now but on all versions past 3.0 for some reason they just hang when starting.

##### **Chenyu** [[00:26:23](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1583)]
Okay.

##### **Wozeparrot** [[00:26:26](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1586)]
So I'm currently unable to start the database. Okay. They need a live access to the database. Yeah exactly, so they're responsible to add a unique or edit blank or just run some hooks by name.

##### **Chenyu** [[00:26:43](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1603)]
Absolutely.

##### **Chenyu** [[00:26:59](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1619)]
as long as the new data looks fine i think it's fine we can discuss later why or which database we should be using next and stuff like that and now it seems to be working yeah migrating to

##### **Wozeparrot** [[00:27:14](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1634)]
something else because influx is also uh there's another issue which is that we can't fetch any data past 12 days great why okay i don't know it's some limitation we'll have okay

##### **Chenyu** [[00:27:38](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1658)]
great so the current status is a new data should be fine and the website is fine

##### **Wozeparrot** [[00:27:46](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1666)]
yes old data exists just not accessible right now new data this is currently it's just temporary while i set up a new database

##### **Chenyu** [[00:27:56](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1676)]
and then i switch it sometime this week okay when you say old data like when was the cutoff

##### **Wozeparrot** [[00:28:04](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1684)]
cutoff was whenever power went out at the office last week okay

##### **Chenyu** [[00:28:15](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1695)]
and did you update all the rock and compatible thing to rock and

##### **Wozeparrot** [[00:28:21](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1701)]
seven i've not yet i've been quite busy fixing provisioning because it's been broken for the past

##### **Chenyu** [[00:28:29](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1709)]
week okay uh cool i think that's fine i don't know probably fine this week we can discuss next week

##### **Wozeparrot** [[00:28:39](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1719)]
i'll bump it before uh hong kong um okay sounds good

##### **Chenyu** [[00:28:49](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1729)]
okay okay uh sounds good okay

##### **Chenyu** [[00:28:57](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1737)]
uh other bounties i think the most notable one is trending stable diffusion where is my wrong my wrong is still going uh any trend it sounds like i have a trend model so

##### **Hooved** [[00:29:17](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1757)]
uh i think it's pretty good yeah you should you should have the uh the eval result for the last checkpoint within like one to two hours probably like one hour ish and uh then it just it'll keep chewing through the checkpoints in reverse order

##### **Chenyu** [[00:29:40](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1780)]
okay uh let's see cool yeah i think uh this is nice this is cool this one is a little bit uh i think the puma took because the system will attack us later is a bit Kei-Ti- Aaron didn't regroup that i'll be uh definitely surprised they didn't fight But now since we know it's been being for, I don't know, seven hours or something, I think reduce that. So let the total end-to-end time drop to 24 hours is reasonable.

##### **Hooved** [[00:30:30](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1830)]
Yeah, I mean, probably most of the compute, even if we drop Beam down, is going to be on the eval. So does that 24 hours just include like the first eval result, which would probably tell you whether it converged or not?

##### **Chenyu** [[00:30:50](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1850)]
I think it was brilliant enough. I mean.

##### **Hooved** [[00:30:53](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1853)]
Okay. Yeah, I can play with, I guess my question for you is, you know, I noticed the Beam parameters, there's like some very specific ones about like the number of UOPs and stuff. And I'm guessing that you arrived at that somehow. Are there any tips there? Like that's probably the key is just playing with those. To rule out any kernels that are, in addition to dropping the Beam down, the main issue as I wrote is like with Beam equals one, there's just kernel or sorry, driver faults. And so maybe I can play with it.

##### **Chenyu** [[00:31:32](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1892)]
So I think this would be really helpful if you can pin down like which kernel FreeNAS quotes, into our stage. Because first, It's very weird that once you rerun the pipeline, the next time it passed, it seems like either there's memory leak somewhere or we have buffer that's not cleaned up properly. Because it doesn't make sense if you beamer kernel, it fails the first time, then the next time it works, right?

##### **Hooved** [[00:32:03](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1923)]
Yeah, no, I agree with that. So there's multiple issues. What I was just talking about a second ago was not related to memory. It's just related to driver fault. But you're talking about memory. So I have in the past pinned down the ones that caused the driver faults, like the exact ASTs and optimizations. I could do that again for the bus errors. But for the actual out of memory stuff, it's just, as I said before, it takes hours to reproduce that. There is some kind of memory leak. I'm not sure how tractable that is. But it is for me to debug. I see.

##### **Chenyu** [[00:32:45](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=1965)]
OK, I think that's more of a TinyGrid core issue, less of a used TinyGrid issue. So I think as long as the script can end to end, recover and show that it still works, it's less. It's not ideal, but at least it works. I think that's nice. And back to your question for the bin parameters, it really depends on. The task under the hood. I don't think we have a very good default there. So usually it's a trade-off between, do you want to look for things that has a lot of local or upcast expression or not? That's essentially what those parameters are. Usually for every parameters, it's a trade-off between the speed versus the search speed. The search time versus the output kernel speed. Since here, I don't know, you say we have like 10x performance gap between in terms of utilization. I imagine that just means a lot of kernels, we are not doing well anyway. I think focusing on good enough parameters that search not as many, but still good enough in terms of end-to-end time would be practical here. OK.

##### **Hooved** [[00:34:13](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=2053)]
Yeah, part of 10x is the power limiting, which might not be an issue on TinyAMD 2. So I could test that. It might shrink down to less than that. And then also, yeah, I'll just play with all those parameters. Yeah.

##### **Chenyu** [[00:34:29](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=2069)]
I think at the end of the day here, what we really want here is if we can first find the exact AST and optimization. So that it crashes the machine. Because that's very valuable for us to fix, that we need to fix anyway. I would say don't worry too much about the power limiting and effect from that. Yes, it's not that big of a deal if at the end of the day, it's just that. But for now, it's like searching multiple hours, which is not ideal to fix.

##### **Hooved** [[00:35:07](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=2107)]
OK. Yeah. OK. We'll look at that. Thank you.

##### **Chenyu** [[00:35:11](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=2111)]
Directionally, I'm pretty happy that this is working. I know it's hard. For the changes that touch core TinyGrad, you can make a decision if you think it should be included in the core thing. I know there are some detect changes. If you find the corresponding behaviors in Torch or Dex, I think we will consider that and add it to the. Add it to the core implementations. If not, you can have it as your custom. That's also fine. But basically, see other than the main loop. See if there are things that you want to be included separately. And I know some of the D type upcast, downcast, it's a hack. Because the way we previously schedule and fuse kernels, that was maybe just faster. So I think we should consider that. Without sacrificing a performance. If you find there's a mismatch between implementations, we should definitely consider.

##### **Chenyu** [[00:36:21](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=2181)]
Yeah. OK.

##### **Chenyu** [[00:36:26](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=2186)]
Sounds good. Any update for RetinaNet?

##### **Flata** [[00:36:32](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=2192)]
Yeah. So I was looking at the EVA script more. I think when I ran. So I think there was a little bit of a delay. I think what I'm running into right now is with JIT not working with the mass select. Because that's a pretty common use case for the EVA script itself. So when I JIT it, I think it's because I know there's a realize that happens inside the mass select implementation itself. So I found that it looks like it's catching the value after you do a couple of runs of that JIT function. So that's when at that point when the tiny Grad Rewritten version versus the current NumPy implementation, does it match? So that's something I put up I think last week. I'm still working through if there's another way to do that. But if I just disregard that issue for now, I think I still find the tiny Grad Rewritten version a bit slower. Or much slower than the NumPy implementation. So I'm trying to see if there's a better way to batch the EVAL itself. Because there's a couple of loops that kind of go through the. The. The. The predictions. So I think there's like the actual per batch loop. And then also inside of that, there's also where they do splits. And then they consider different levels on each of those predictions. And then that's when they start doing a lot of the operations from there. So I think those are kind of like the two main issues that I really want to try to solve.

##### **Chenyu** [[00:38:00](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=2280)]
So I am reading the mask select implementation. I don't see any realize here. But I do notice that the counts in that function doesn't have device specified. I think that might cause issue.

##### **Flata** [[00:38:16](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=2296)]
Oh, yes. I think also I was trying to do the multi GPO case. Yeah, there is something that's not working there where it's complaining about the devices should be in the same. Or like all of the buffers should be in the same device altogether as well. Yeah.

##### **Chenyu** [[00:38:32](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=2312)]
So those we definitely want to fix. And if you notice these, feel free. To open a separate PR that fix this with some tests. Okay. Yeah.

##### **Flata** [[00:38:44](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=2324)]
And also going back to the realize one. Yeah, I meant I think it was like, I think there's one line of the code there on the mass. Health implementation where they do the dot item actually. So that's when they create the the I guess the accumulator. I think for for getting the indices. Yeah.

##### **Chenyu** [[00:39:02](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=2342)]
Okay. Now it yes, we should not be doing.

##### **Chenyu** [[00:39:09](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=2349)]
Okay. I don't understand. Isn't this just a sum or something? Okay. I don't know. Yeah. I can take a look or you can take a look. I think I think this needs to be fixed. The device definitely need to be fixed and we shouldn't go. Realize or make any if we don't need to.

##### **Flata** [[00:39:27](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=2367)]
Okay. Okay. Sounds good. Yeah, I'll I'll talk to a simple copy about this because I know he worked on the initial implementation and see if we can kind of whip up something together and hopefully we can remove that. Okay. I guess that dot item call there.

##### **Chenyu** [[00:39:40](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=2380)]
That's good. Okay. Anything else wish to include? B1TG are you working on anything?

##### **B1tg** [[00:40:03](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=2403)]
I was doing the FP8 bounty. And the last part is get the. Yeah. I don't get access to the red machine. Maybe. Maybe I can get access to.

##### **Chenyu** [[00:40:27](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=2427)]
Oh, sure. What Barry can you? Add him to. I don't know which one support FV8. But add him. Add him to whichever.

##### **B1tg** [[00:40:38](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=2438)]
On the green machine.

##### **Chenyu** [[00:40:44](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=2444)]
Okay. We will figure this out and get you access to a machine.

##### **Flata** [[00:40:48](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=2448)]
Okay.

##### **Chenyu** [[00:40:57](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=2457)]
Anything else? Checking the bounty. 8. Checking the PR. Okay. I don't have anything. Or other people in this call. Anything else?

##### **Flata** [[00:41:30](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=2490)]
No. Okay.

##### **Chenyu** [[00:41:48](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=2508)]
I think that's about it for this meeting. And next week it will be pushed back by 3 hours. And that's all for today. Thank you, everyone. See you next week. Thank you.

##### **Flata** [[00:41:58](https://www.youtube.com/watch?v=IuaE1LK9_SQ&t=2518)]
Bye.
