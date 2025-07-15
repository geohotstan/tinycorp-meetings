# 2025-07-14 Meeting

### Meeting Agenda

**Time:** 9am Monday San Diego time
- company updates
- kernel refactors
- hcopt refactors, mlperf llama 405b
- viz tool
- drivers
- cloud
- onnx
- symbolic stuff
- other bounties

### Audio

[Youtube Link](https://www.youtube.com/watch?v=7hyHb7LBF9M)

### Highlights

- **[Company Updates](#geohot-000000)**: All four new AMD machines are now operational and available for use.
- **[Kernel Refactors](#geohot-000041)**: Major refactoring is underway to create a cleaner kernel representation by explicitly ending ranges, using `define_reg`, and removing `ones` to ensure ops work consistently across small and large graphs.
- **[hcopt Refactors](#chenyu-000130)**: Hand-coded optimizations (`hcopt`) have been refactored for readability and flexibility, now using absolute axis positions. This allows for more advanced reordering (e.g., moving upcasts before reduces) and unexpectedly improved openpilot performance.
- **[Kernel Refactors](#geohot-000507)**: A new approach for labeling axes (e.g., `global one`, `reduce zero`) is being adopted to make optimizations invariant to the removal of size-1 dimensions.
- **[MLPerf Llama 405B](#chenyu-000810)**: For the Llama 405B evaluation, it was confirmed that the data loader concatenates all datasets into one large stream and evaluates with a sliding window, explaining the strict evaluation order requirement.
- **[MLPerf Llama 405B](#geohot-001000)**: To meet the AMD contract goals, the primary focus for Llama training is on optimizing the performance of the GEMM and flash attention kernels, alongside implementing multi-node support.
- **[Viz Tool](#qazalin-001135)**: Graph rewrite steps can now be visualized using the `tiny-device`, providing better insight into the transformations applied during `get_program` and `get_schedule`.
- **[Viz Tool](#qazalin-001208)**: The visualization tool now renders graphs in a separate stream, fixing display issues with multi-graph programs and showing kernel execution timelines across different devices.
- **[Viz Tool](#geohot-001337)**: There are plans to enhance the viz tool with more detailed profiling data, such as SQTT traces and performance counters (e.g., L2 bandwidth), to better diagnose kernel performance bottlenecks.
- **[Drivers](#geohot-002040)**: The next priority for driver development is to enable fast data copies between storage and GPUs and to implement optimizer weight offloading, which requires efficient use of pinned CPU memory.
- **[Drivers](#chenyu-002531)**: It was suggested to test the copy overhead and optimizer offloading performance by running a BERT model on an MI300X with its optimizer state kept on the CPU, simulating the Llama 405B workload.
- **[Cloud](#wozeparrot-002736)**: The cloud file system is slow and blocked on merging hashing improvements from `tiny-grid`. This is delayed by a machine-specific hashing bug on AMD that needs to be resolved first.
- **[ONNX](#chenyu-003122)**: The `load_onnx` implementation is blocked by a failing test in openpilot involving a constant-folded, shape-changing bitcast. A workaround is needed to unblock merging the new ONNX support.
- **[ONNX](#chenyu-003502)**: A correctness bug in an ONNX up/down-sampling operation was exposed by recent `hcopt` refactors. The issue, previously thought to be device-specific, needs a proper fix to ensure correct behavior on all platforms.
- **[Other Bounties](#b1tg-003626)**: A flaky bug causing a core dump has been reliably reproduced in a Docker environment after several hours of testing. A GitHub issue will be created to track the investigation and fix.
- **[Kernel Refactors](#ignaciosica-004143)**: It was suggested to define the local memory layout during initial shape tracker creation rather than using later permutations, which would ensure the layout is always valid.
- **[Other Topics](#geohot-004709)**: A brief analysis of the Luminal project was shared, noting its strong foundation in e-graphs for algebraic pattern matching and its clean representation of loops.

### Transcript
##### **Geohot** [[00:00:00](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=0)]
Okay. Any update? Step to the bottom of the screen. We soldered red in the green last week. Got a few more greens being dealt. Yeah, we got all the AMD machines are off. One, two, three and four. Where? So, you can go wake. Anything quick for your factors?

##### **Geohot** [[00:00:41](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=41)]
Yeah, I think there's a few things that are finally like being made correct. There should be no reason that you only have a... There should be no reason that whatever you're building doesn't work in a big graph as well as the small graphs. And the key thing to realize is that stores and loops. It doesn't even have to be stores. I can have an end range. But like the way that I was implicitly ending the ranges didn't really make sense. So by explicitly ending ranges and then fixing to find ACC to be defined reg, doing all the other things about removing the ones. I think then we have a really beautiful. A kernel thing that can express all the things that like, like, hey, like, can it stop?

##### **Chenyu** [[00:01:30](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=90)]
Yeah, I guess to the related thing. So I did bunch of in co-optimization, reflectors. I think it's a bit. I think now is a lot readable and it's more flexible to... So I think at the end of the list, it should be able to support moving upcast to before reduce. For now, those games no longer... It's not taking relative positions, but like taking from the absolute position. So it doesn't... It's invariant even if you like, they're differently. And also it should be also... Also, I know skip the ones. So let's... If later we want to introduce not doing simplifying ones in between up-up, let's also invariant and should just work. So we should be able to remove all the reference to the first underscore, reduce, and first underscore upcast. And basically you can reorder it however you like. Then you can move the upcast to before reduce and after the global no-cause.

##### **Geohot** [[00:02:49](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=169)]
Great. Yeah, I think I also have to make changes in the GPU dim thing to allow global and local to be in any position.

##### **Geohot** [[00:02:57](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=177)]
But I think when that's done, we have a much cleaner approach down the...

##### **Chenyu** [[00:03:05](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=185)]
Where is that being for putting on other land? First take. I guess I'm to place. Also another thing is we previously have the idea of the axis into unrow or anything reduced related is relative to your first reduce. But if we want to keep once then something needs to be changed there.

##### **Geohot** [[00:03:38](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=218)]
It's minor, it's quite fine.

##### **Chenyu** [[00:03:42](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=222)]
Because previously we would remove that left over one after if we say unrow the whole X-reduce axis.

##### **Geohot** [[00:03:52](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=232)]
Yeah, I think that that's where no real rush to do that. But in general one should just be banned from everything. Like there's nothing, there's no...

##### **Chenyu** [[00:04:06](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=246)]
What do you mean by one should be banned?

##### **Geohot** [[00:04:10](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=250)]
Well, so you can draw the distinction between removing the ones from the shape from what you really want to stay invariant is just the name of the axis. So as soon as the AST comes into kernel you can just label the axis like global zero, global one, global two, reduce zero, reduce one. And then whether you actually keep the ones in the shape or not is kind of irrelevant. But in general, like there's nothing that ones really should be doing.

##### **Chenyu** [[00:04:44](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=284)]
But the decision, we need to make a decision to do we remove it as soon as possible or do we remove it as late as possible? Because... Yes. So...

##### **Geohot** [[00:04:56](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=296)]
If we want to keep the shape length... I don't think we have to change it. I don't think we have to change it as early as possible.

##### **Geohot** [[00:05:07](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=307)]
Yeah. I don't think it's that important. I think that like what you really want to change before you think about whether you're removing the ones or not is just how we label axes. So right now we just label the axes like it's the argument in the opt-off. It's like zero, one, two, three. But like so one, this is going to have to change a bit for reduces. Because if you have like three reduces in a kernel, how do you know which opt-off refers to which reduce? And then if you like make it so that you label the axes like global one, and that just always is global one, global one might be removed if it becomes ones. But like what won't happen is that like global two will shift over and become global one. It'll always stay global too. So it's really more of a naming thing than anything to do with the actual ones. And we have to address the naming thing in some way anyway.

##### **Chenyu** [[00:06:10](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=370)]
Yeah, so it sounds like it's easier if we keep ones as low as possible. Probably, yeah. You want to make it low core right? So you need to look at the thing and be able to tell okay, the one has been removed. So the actual first one is being them too. Yeah. Okay. Anyway, that was that was the direction I want anyway. They will make a lot of. The first thing simpler too.

##### **Geohot** [[00:06:39](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=399)]
Yeah, we have a whole bunch. There's a whole bunch of hacky code that like detects if I made the axes go away, then do this.

##### **Chenyu** [[00:06:47](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=407)]
So I think I remove almost all of it. The only one that's left is at the end of a local detection because it needs to do like local correctly, but let's also go away once.

##### **Geohot** [[00:07:00](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=420)]
Might be keep ones. Oh, okay. I've been saying in theory. Okay. Sounds good. So let's also hand co-optimization.

##### **Chenyu** [[00:07:31](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=451)]
I also changed some behavior slightly. The initial idea was so like it as long as it doesn't hurt open pilot is fine to remove. But after I put on move bunch of stuff open pilot got faster. Whatever. Great. Yeah, I mean like there are there are some optimization that was just wrong. Or maybe at the time it was put it was right, but logically it's wrong and I remove all those and something become faster.

##### **Geohot** [[00:08:03](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=483)]
I totally believe that. Yeah, that's some of the oldest like crabby is code. Nice to see you getting cleaned up.

##### **Chenyu** [[00:08:10](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=490)]
Yeah, so I'll probably do this for a few days. Then go back to lama for a while. I was able to run their data loader. I can confirm now that when they do e-vail, they just cat everything together. Make a very big dream and evolve on that thing. So I can like just replicate that. And I discussed this was was parrots that. Or it's I think that's the main reason they need the e-vail order to stay the same because they just get everything together.

##### **Geohot** [[00:08:46](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=526)]
And then at the end of the pad zeroes are. No, so.

##### **Chenyu** [[00:08:55](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=535)]
Everything except the first few tokens after the first few tokens it becomes the four. It would because they cat everything so it's a sliding window and that's that window would be four after the first max then. And I think for the first few digits pad.

##### **Geohot** [[00:09:19](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=559)]
Yeah, I mean we should just this should always be basically one size.

##### **Chenyu** [[00:09:23](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=563)]
Yeah, the main reason I want to understand this is I just want to implement it. Otherwise Nemo or make out from is very hard to use because we are running let's. Then a media machine and it pretty much just assume a lot of. And then stuff that we need to mark so the code we're on. That's annoying. Yeah, we don't probably don't let. So yeah, we'll get back to this later. Or I don't know if someone is more. Knowledge. I want to help. Oh, so we're.

##### **Geohot** [[00:10:00](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=600)]
Anyway, you know, overall I'm you know just think of through the whole AMD contract. I think I think we're in a pretty good place if you could get the stuff training. It's really only two kernels that I have to make fast. I have to make the gem fast and I have to make the flash attention fast.

##### **Chenyu** [[00:10:17](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=617)]
And we need to make everything.

##### **Geohot** [[00:10:22](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=622)]
Well, okay, and then there's there's the multi stuff. Which. It shouldn't be too bad. We're getting the network cards put in this week.

##### **Chenyu** [[00:10:34](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=634)]
I think a lot of this is in addition to those two kernels are some of the scheduler stuff we definitely need to revisit. Is it. It's not just multi or I is like why is the single kernel softmax not working?

##### **Geohot** [[00:10:54](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=654)]
Wait, the single kernel softmax works.

##### **Chenyu** [[00:10:57](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=657)]
It just doesn't work. I know it takes lots of room for some reason because something was not done correctly. Oh, no, I do what it is.

##### **Geohot** [[00:11:07](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=667)]
I thought I fixed that, but either way, that should be an easy fix now. If there's still a problem with that, I thought I fixed the thing with all the fuse logic just doesn't need to be there. We can like to lead all the fuse logic now that we have like contiguous.

##### **Geohot** [[00:11:22](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=682)]
Okay. Okay, anyway, what was that? We can move on to this.

##### **Qazalin** [[00:11:35](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=695)]
So I merged the graph rewrites on your all the get program and get scheduled course. So you can see again, for in graph, or for the rewrites steps, the tiny device.

##### **Geohot** [[00:11:51](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=711)]
And I really like the tiny device. If you want anything else, just let me know I can add it to the tiny device.

##### **Qazalin** [[00:12:08](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=728)]
And I also did some work on the graph. So now graphs are a separate stream. That also fixes the issue with like multi graphs and Nvidia machines and AMD. So, yeah, you can see at the top in each device series, the expanded batch, which in metal, we just like evenly spaced them. We don't really know which one finishes first.

##### **Geohot** [[00:12:38](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=758)]
Well, so for the multi graphs instead of making them a separate stream, I haven't I haven't looked at what you did yet. But like the obvious thing that I would think to do is to like put them on their right device to like pull them out of the graph.

##### **Qazalin** [[00:12:54](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=774)]
It's pulled out in each of the device streams, but then there is a big.

##### **Geohot** [[00:13:01](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=781)]
Oh, I see we said yeah. From this. I just got to look at this, but yeah, that makes sense. Yeah.

##### **Qazalin** [[00:13:12](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=792)]
So when you dispatch like the graph commands, whatever there is a graph stream that spans the entire across the devices and within each device, there is the kernel that finishes. And Nvidia and AMD, we know exactly when the kernels finish in metal. I don't think there's a way to get that.

##### **Geohot** [[00:13:32](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=812)]
So I just evenly spaced it.

##### **Geohot** [[00:13:37](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=817)]
Yeah, I mean, I think what we want to what we want to think about with this is how to start pulling out more of the profiling data and making it making a visible. Like kind of like the stuff that they have in radion graphics profiler, I put the sqt stuff.

##### **Geohot** [[00:13:59](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=839)]
See, I think it's like we need to be assembly. It's related to what? The programs.

##### **Geohot** [[00:14:09](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=849)]
Well, so the sqt t stuff will give you logs of when each compute unit launches. So you can actually see like right now we have a kernel and a kernel has times, but you can break that kernel down. You can break that kernel down to like when each global is launching basically. And then also the plots that show things about the kernel that talk about like the how much l2 bandwidth is using, how much ran down with it's using. We should have a whole bunch of like performance counters for that. And then if we can expose that stuff and viz without adding overhead like this is ideal.

##### **Geohot** [[00:14:57](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=897)]
A full sqt t tray seems like it adds a lot of overhead, but I think we can do a lot of stuff without the full trace. Like I guess what it's really getting at is like, okay, so we have a kernel and the kernel takes 12 microseconds. Why does it take 12 microseconds?

##### **Geohot** [[00:15:34](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=934)]
Like does it take 12 microseconds because it's limited by ran bandwidth because it's limited by CPU because it's limited by l2 because it's not efficiently using all utilized registers.

##### **Geohot** [[00:15:52](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=952)]
And then how the how the RAM stuff coming that make it the RAM looks.

##### **Qazalin** [[00:16:02](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=962)]
So for the RAM stuff, the problem is that right now when you get a model, the memory scheduler gets an allocates a big chunk. And because it's like not really in a you up spec like it's operating in a schedule item level, you don't really know which offer that is you just see like a giant blog.

##### **Geohot** [[00:16:32](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=992)]
Well, so it's a giant block, but they should all have offsets right. Yeah, there's a buffer. You're saying try on the sub of them.

##### **Qazalin** [[00:16:47](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1007)]
Yeah, I guess I could do that, but it's not like this sub buffers free anything so the whole chunk just stays alive. So it's getting out and reallocated.

##### **Geohot** [[00:17:14](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1034)]
We need to do better with sub buffers in general. In test grab, it's a pretty good job of this that you could any input to any kernel could be a buffer view. So I'm not sure if this is being done at the you off level with the memory planner. I feel like it might not be. And maybe we have to fix that.

##### **Qazalin** [[00:17:35](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1055)]
It is not just being the schedule item and.

##### **Geohot** [[00:17:42](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1062)]
Yeah, like I think that's we want that we want the memory planner to do this at the you off level and then like everything should support buffer views as inputs.

##### **Qazalin** [[00:17:52](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1072)]
So.

##### **Geohot** [[00:17:58](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1078)]
Oh, like the buffer view. Oh, yeah, like when you have the things in the kernel are like, wait, it can go to.

##### **Geohot** [[00:18:07](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1087)]
Like you can have like a buffer is an input or an m stack is an input or an m select is an input that should also support buffer view was an input.

##### **Geohot** [[00:18:29](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1109)]
I'll paste what it is in test grab.

##### **Geohot** [[00:18:34](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1114)]
I also fixed I pull out the defined bars from the graph and I put them in the overworld. So like the kernel is a kernel has like a defined bar like as now it has an input in the end of the graph.

##### **Qazalin** [[00:18:49](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1129)]
Yes, literally what happens in the kernel. Yeah, it's like an art to the kernel. So you just pull it into the correct.

##### **Geohot** [[00:18:57](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1137)]
Yeah, it's what in the graph. Yeah, that makes a little sense. Oh, anything else for this.

##### **Qazalin** [[00:19:14](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1154)]
I think the tiny devices in a good spots all transition to the GPU specific metrics. Those are the materials. Also see what we can do with the refactures to make the memory plan more debunkable.

##### **Geohot** [[00:19:37](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1177)]
Out of that. Okay, let's move on to drivers. Yeah, so I've ported and we'd be sharing to 15 90 and 30 19. So it's still not in CI.

##### **Nimlgen** [[00:20:05](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1205)]
I need to test this better with both the 15 19 and 30 19 before it in them.

##### **Geohot** [[00:20:16](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1216)]
So yeah, I think I'll finish with the CI this week and I'll start on. I know what's what's high priority and we decoder or some MD performance stuff. Probably AMD performance stuff.

##### **Geohot** [[00:20:40](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1240)]
Yeah, getting like so we have the machines now. So we should put better drive in the new machines. I don't know if you checked out AMD 3 and 4 of the drivers. But yeah, getting getting fast copies from the drives to the GPUs and then starting to work on optimize or wait off loading. I think it's probably the next type priority thing. So being able to quickly, like being able basically to to use pin CPU memory. Because I think none of our stuff is pinned right now.

##### **Geohot** [[00:21:19](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1279)]
Like in some ways, all memory we create on the CPU device should be pinned memory. Yeah, okay, but I believe.

##### **Nimlgen** [[00:21:40](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1300)]
Yeah, okay, I think yeah, we can do that. But here we have several devices. I think we don't know to reach we should be.

##### **Geohot** [[00:21:49](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1309)]
But I don't think.

##### **Geohot** [[00:21:52](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1312)]
But I don't think that the pin memory works.

##### **Geohot** [[00:21:54](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1314)]
I don't think you have to pin it to a device, right?

##### **Geohot** [[00:21:56](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1316)]
I think you're just pinning it to a physical page.

##### **Nimlgen** [[00:22:01](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1321)]
Yeah, but I'm not sure like could I can use it. Like I said, it's a pin memory because could have had a special API to look at pin memory.

##### **Geohot** [[00:22:12](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1332)]
Yeah, but our PCI driver should be able to use it right? Yeah, that's for sure. We already have a pin memory for copy ads. Really? Yeah, really? But you sloped my pro. I guess math locked is pinned memory. Yeah, are we getting basically or are we getting the full PCIe speed is kind of what I'm saying. Yeah, I mean, I'll double check that.

##### **Nimlgen** [[00:22:54](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1374)]
But the last time when I check that, yeah, we do get what mean we basically do two copies right now because we kept it from the like the CPU into pin memory. And after that we do DMA and DMA is has higher speeds and yeah, close to PCIe speeds. So we are basically limited. So yeah, I'm hoping on this CPU.

##### **Geohot** [[00:23:21](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1401)]
Yeah, what I would play with is moving the.

##### **Geohot** [[00:23:25](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1405)]
Which is like doing basically if you understand what the optimizer weight offloading is.

##### **Geohot** [[00:23:32](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1412)]
Well, like the optimizer like the M and V offloading. You know, check that. I was still there.

##### **Geohot** [[00:23:56](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1436)]
I mean, like, so you have this you have this like big tensor like like a like a terrible like how quickly can we copy a terabyte from the.

##### **Geohot** [[00:24:15](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1455)]
And the end GPUs to the CPU and the CPU back to the end GPUs. Yeah, okay, so yeah, okay, I'll measure it like this.

##### **Nimlgen** [[00:24:30](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1470)]
Yeah, basically, we I think we already can achieve like this like the full PCIe bandwidth when we just use system memory and we just read from system memory directly or use D made.

##### **Geohot** [[00:24:46](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1486)]
Yeah, so I mean, yeah, I'll check that.

##### **Nimlgen** [[00:24:53](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1493)]
I mean, basically we can already allocate like the Pint memory and we just put push them to these DMA. And I think speed is already good because the like the last time I looked at that.

##### **Geohot** [[00:25:09](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1509)]
So the limit equals the. Call the CPU to CPU code. May we can just get rid of this type. I think we should get the full bandwidth.

##### **Chenyu** [[00:25:31](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1531)]
So I think what we can ask maybe the easiest way to test something like this is we can take birds then move birds. Optimizer state to CPU before training and we start training like that and see how much of copy overhead we are getting our M 300 X. That would be very similar in terms of what we want for llama 405 B because 45 is so big that the off-matter state need to be state in system rate. Anyway, making sure like copy is fast from the initial weight loading from disk to GPU is fast then GPU state is GPU tensor to CPU and back is fast.

##### **Geohot** [[00:26:27](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1587)]
I think that's why you. Yeah, okay, sounds good. Anything else? I don't know. To cloud. I've been going through UV and PRs. Mostly okay.

##### **Wozeparrot** [[00:27:04](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1624)]
I think you might want to split the failing test. Just into a separate PR.

##### **Geohot** [[00:27:14](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1634)]
I don't know if it needs the other stuff in the cross-host graph PR. Okay, I see. I see. File system is hosted somewhere now.

##### **Wozeparrot** [[00:27:36](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1656)]
Work this week. It's just on the one year eight, the one node. I really have reserved for cloud. It's pretty slow right now. I need to merge hashing in main tiny grid. Get it fast. For some reason, the hashing tests, the cac tests are broken.

##### **Geohot** [[00:28:14](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1694)]
And on your branch over. And on master.

##### **Wozeparrot** [[00:28:19](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1699)]
On master. And it seems to be my machine specific. Not sure what's going on there.

##### **Geohot** [[00:28:26](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1706)]
And it seems to be AMD specific as well. Great.

##### **Chenyu** [[00:28:35](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1715)]
Yeah, I think. Maybe it's related. Maybe it's not when I was messing around with hand co optimization. Some on next test just fail apparently the behavior and correctness was dependent on doing some uptest.

##### **Geohot** [[00:28:52](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1732)]
I think something is not correct. It might be that.

##### **Chenyu** [[00:28:58](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1738)]
Or you're just test with no opt and then test on the same machine with different device.

##### **Wozeparrot** [[00:29:06](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1746)]
Yeah, with different machine with L of the M at works. I'm wondering if it's just fusing stuff too much and then you get like a really big constant.

##### **Geohot** [[00:29:22](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1762)]
So if that's the case issue workforce. Yeah. Yeah. We were handling like a casting them didn't 64.

##### **Chenyu** [[00:29:45](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1785)]
Yeah, that's for index right now for const.

##### **Wozeparrot** [[00:29:49](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1789)]
Yeah, I feel a big constant in the code.

##### **Geohot** [[00:29:51](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1791)]
I don't think we do that. Yeah.

##### **Wozeparrot** [[00:29:58](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1798)]
And I've seen constants from like other hash related stuff be like extremely large like.

##### **Chenyu** [[00:30:08](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1808)]
Large large for like large land long or like large land long long. Great.

##### **Wozeparrot** [[00:30:20](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1820)]
If it's larger than long long the compiler will air out and say that it doesn't fit.

##### **Geohot** [[00:30:27](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1827)]
Okay, but that's not a way. If it's just larger than long. Okay. Okay, anyway, it's like a bug.

##### **Qazalin** [[00:30:42](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1842)]
Okay.

##### **Geohot** [[00:30:43](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1843)]
Uh, they. Anything else? Hello. So file systems later it's low in his hatching to be fixed. Have something through AMD. Great. Okay, next on next.

##### **Chenyu** [[00:31:22](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1882)]
So I merge low on next taking IO system. And so we have a very big maker.

##### **Geohot** [[00:31:31](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1891)]
Next. Okay.

##### **Chenyu** [[00:31:38](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1898)]
Yeah, so we discussed this before. Let's try to fix the on X. Seeing that hero or come out reported first.

##### **Geohot** [[00:31:49](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1909)]
We really want to keep. Is it the big cast thing? Yeah, this is a big cast. Yes, the work. The work around was some big cast thing. I think that buffer view in the schedule might fix this. I buffer view in the over graph. Does it take to add that or remove the code?

##### **Geohot** [[00:32:19](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1939)]
Well, I think it's just we're not really like always strict about how we handle that bitcast.

##### **Geohot** [[00:32:26](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1946)]
But I think if we just always put it on the buffer view, then it's good. The problem is that you have to make this cast the. Kind of boundary, but that's what buffer view used to do. It makes this cast it. It's the.

##### **Geohot** [[00:32:50](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1970)]
Yeah, I mean, it shouldn't always have to be is this what is this like shape changing bitcast in the kernel? I'll have to look at the failing test. But I'm not sure we should block on X on this.

##### **Geohot** [[00:33:00](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=1980)]
But we should definitely look into this supporting open pilot two cases very important. Yeah, it's kind of constant fold the shape changing bitcast. Yes.

##### **Chenyu** [[00:33:24](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2004)]
So I guess just find some good enough worker on to fix master for open pilot use case.

##### **Geohot** [[00:33:36](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2016)]
I think that's important. Then this I how to fix this better. In that case, I think my fix works.

##### **Wozeparrot** [[00:33:52](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2032)]
We have any regression current code won't handle constant folding shape in your back has anyways.

##### **Geohot** [[00:33:58](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2038)]
Oh, okay. And. And we just do that and disable that rewrite rules for constant or something. Yeah. Okay. Let's let's get that fixed because the issues always.

##### **Chenyu** [[00:34:20](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2060)]
In order to previously when we remove value hack. We are also doing lots of refactors here and there and change stuff. So if our only important client stop using the latest version, it might get more difficult to bring it back.

##### **Geohot** [[00:34:35](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2075)]
So let's try that and hopefully there's no other issue. Then yeah, I will review the big on next thing.

##### **Chenyu** [[00:34:49](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2089)]
I think we are getting pretty close to get emerge. I will check the API.

##### **Geohot** [[00:34:57](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2097)]
And also I mentioned earlier, there are some that.

##### **Chenyu** [[00:35:02](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2102)]
I think it's up. Up simple or down sample one of the size changing stuff that might depend on. I so currently a speed disable on some device, but let's not correct because if you change the hand co optimization code, it also fail on other device. So it's not really like device dependent and we should get. To the button of this. Because it's not a function that we don't support. It's either we say we don't support or. We support it correctly, but we shouldn't say we support and output is wrong because that's very annoying.

##### **Geohot** [[00:35:40](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2140)]
So. And that's our next. Next symbol for. It's like, oh, you don't say something. No, really. And at one time to recognize. Okay. Let's find. And.

##### **Chenyu** [[00:36:11](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2171)]
X we have other ponties. Oh, let's go through the familiar faces in the meeting.

##### **Geohot** [[00:36:22](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2182)]
B one key. Do you want to see something?

##### **B1tg** [[00:36:26](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2186)]
Oh, I was reproducing the audit flag key and you can see the message I send in the journal. Record a code dump of the person process. And the process. Recommend for at the metadata set up.

##### **Geohot** [[00:36:50](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2210)]
In the see Python function. I see. And the.

##### **B1tg** [[00:37:00](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2220)]
I found this bug exists before the only. It's the same thing.

##### **Geohot** [[00:37:06](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2226)]
I put links in. Not sure it's a person bug or. Any grade bug. I don't really know about this.

##### **Chenyu** [[00:37:40](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2260)]
I guess first because we don't have a way to reliably reproduce this. But you're saying it's not fixed by. Whatever. Or correct that puts the tensor on Python device that would that didn't help.

##### **B1tg** [[00:37:58](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2278)]
Yes, it's still occurs. I reproduce in the dog content. Run the run the test multi times. I could one or two hours.

##### **Geohot** [[00:38:12](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2292)]
It will reproduce. Uh. So this flag is reproducible. If you run in the test, out of times.

##### **Chenyu** [[00:38:44](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2324)]
See, okay, I think for this one, let's maybe create a issue and you can paste all your stuff. You're findings there and we can discuss in a thread. For now, I cannot give you anything better than I will take it.

##### **Geohot** [[00:39:00](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2340)]
Okay.

##### **Chenyu** [[00:39:01](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2341)]
Yeah, let's. So as long as you have a way to kind of reliably test. So we know if the issue is. Or not. I think that's a good start. Then I think it's good if other people can also reproduce the issue. And we can discuss on the issue thread. You see like. What's the possible way that we fix this.

##### **Geohot** [[00:39:25](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2365)]
I think so. I think so.

##### **Qazalin** [[00:39:28](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2368)]
Okay.

##### **Nimlgen** [[00:39:33](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2373)]
That's how you have anything to say.

##### **Wozeparrot** [[00:39:37](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2377)]
Not a whole lot of progress to speak, hopefully getting back into making sure the correctness is good for the for the eVal script.

##### **Geohot** [[00:39:45](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2385)]
So I'll provide more updates later on.

##### **Qazalin** [[00:39:48](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2388)]
Okay.

##### **Geohot** [[00:39:52](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2392)]
Ignacio Sica to say something.

##### **Ignaciosica** [[00:39:57](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2397)]
No, no, no, no, no, really anything from my side. I've been mostly following George Refactor so over Colonel. And yeah, that's it.

##### **Geohot** [[00:40:09](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2409)]
I think I think access types is like kind of what you were going for.

##### **Ignaciosica** [[00:40:14](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2414)]
Yeah, that was really good way of solving the issue was in concert or I think the. It's a more general way.

##### **Geohot** [[00:40:25](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2425)]
Yeah, I mean, I got that. I got I reading your PRs are mostly like how I came up with that. I'm like, well, we just have like just an array and we just track the access types. Like this isn't that hard. Yeah. Yeah, I think I think it's pretty nice now. I think I'll remove those. There's those two stupid methods still in Colonel info that tell you the number of globals and the number of locals. Although that refactor today. So then GPU dams won't have that either and we'll just use the access types.

##### **Ignaciosica** [[00:40:52](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2452)]
Yeah, it's great. It's it's it's it's really getting pretty clean. Everything.

##### **Geohot** [[00:41:01](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2461)]
I think so. I really like the distinction also between a ten year and a. I brought this up yesterday the distinction between global and loop. Like we previously had no way of expressing loop in a GPU kernel, but there's nothing that says you can't use loop. There's nothing that says I can't make a loop around my whole GPU kernel like dispatch that is one global. So now we have like a different access type for those two things and it should all just work. Yeah, I'll also once once the first reduce and first up cast first outcast things are gone. I'll write some tests that. Premiate order internally and everything should be fine.

##### **Ignaciosica** [[00:41:43](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2503)]
Great. I once I once think I wanted to mention that I saw in your metal you up or a hand coding to the SM loading. I don't know if you want to express the local layout through the permutations jointly with a loading and storing, but you want to do that beforehand. A permuting all these strides like the order of the axis like not permuting after hand, but in the initial stage you want to permit the. The order of the axis like you want to be able to need that that. Role major column major or in any order you want rather than a relange or not permutation later. I don't know if that makes sense at all, but that's like the only thing I.

##### **Geohot** [[00:42:37](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2557)]
Don't really follow that so you can purview there's three shape trackers involved. There's the load from global memory, the store to local memory and the store from local memory. And you can permute all three of those and they all kind of like mean different things. There are invalid permutations of them and we might want to make it more restrictive to not allow those invalid permutations. But like another way to think about the initial load and stores that that's a copy. And then you can actually do those things in any order you want. So you can you can like arbitrarily permute as long as you permute those two shape trackers together. And then for the store and the. The read the store to local and the load from local you can permute those two and those will determine the actual layout in the local memory.

##### **Ignaciosica** [[00:43:28](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2608)]
Yes, but I think if you later permute like the store and load from local memory there you're there are going to. And counter some invalid permutations that you don't encounter if you like order the access from the beginning. Like right now if you initialize the shape tracker from shape, I think it will initial in it like column major. But you can like define that local layout in that stage not recurring a permutation later and that is always valid.

##### **Geohot** [[00:44:06](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2646)]
And I see what you're saying. Yeah, I'll think about that. Okay, so you're saying basically to bind the layout to the to the to the memory and not to the not to the load store.

##### **Ignaciosica** [[00:44:20](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2660)]
Yeah, you can do that like first. And that is already because they both start like the same right.

##### **Geohot** [[00:44:29](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2669)]
That makes sense. Yeah, I mean, I'm doing so I'm doing I'm unifying the main thing I'm going to work on this week is unifying the defined them. Define reg to be the same as the others. And then I think will see a lot of stuff about this as I replace like reduce with loads and stores from define reg like that thing I posted in theory. It'll just be the same logic. So whatever I do there will will copy. But yeah, no, I think I agree that there might be something kind of like the way that I use reduce in order to generate those. There might be something for the locals as well that can't be invalid because yeah, I agree it's annoying that you can ever specify something about.

##### **Geohot** [[00:45:10](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2710)]
That computer should do that. Okay.

##### **Qazalin** [[00:45:17](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2717)]
Okay.

##### **Geohot** [[00:45:20](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2720)]
Okay.

##### **Chenyu** [[00:45:22](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2722)]
It's near right less our regular list. I don't think we have any.

##### **Geohot** [[00:45:30](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2730)]
Let me check.

##### **Geohot** [[00:45:41](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2741)]
I said a few of the refactor boundary. I mean you basically took the moving the dims one I took the define reg one congrats to cordists for claiming the first refactor bounty. And here's another one locked here. So I think there's been some good progress there as well.

##### **Geohot** [[00:46:03](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2763)]
Yeah.

##### **Chenyu** [[00:46:10](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2770)]
Let's try to everyone on this meeting. Let's try to close some peers. Yeah, a lot of peers. But I think that's it.

##### **Geohot** [[00:46:32](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2792)]
I want to say something about the different approaches to tiny crevices. I forgot. Domino.

##### **Chenyu** [[00:46:55](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2815)]
Or if anyone in this meeting has questions about any great now it's a good chance for you to post in either general or the chat of this meeting is fine.

##### **Geohot** [[00:47:09](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2829)]
Yeah, we should invite well by Joe to the next meeting. I want to present any of the differences with with luminal. I read the luminal code. I mean the main thing that the whole thing is very much based around e graphs, which is kind of nice. And like one of the things that the e graphs do really nicely is the right side of our pattern matters is arbitrary turn complete code is lambdas. But it doesn't have to be you could imagine our pattern matcher being a you pat to a you pat and like then it's an algebraic transformation and not a arbitrary current turn complete code transformation. So I like the syntax that the e graphs used to. So yeah, they're basically based on e graphs. They have a bunch of rewrite rules. Now it's very it's just starting out. And they're focused on just like they want to do like big speed of kernel search. They also have they handle looks pretty nicely. They have loop in and loop out. They get to get they don't need their loop in to have to have a step. I think I'll eventually remove that, but the loop in the loop out is a pretty nice way of expressing it.

##### **Geohot** [[00:48:23](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2903)]
In my experience reading, and then their fun end is very very incomplete.

##### **Qazalin** [[00:48:43](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2923)]
Okay.

##### **Geohot** [[00:48:45](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2925)]
I don't see any questions. I don't see anything else.

##### **Chenyu** [[00:48:49](https://www.youtube.com/watch?v=7hyHb7LBF9M&t=2929)]
So let's say for this meeting. Thank you everyone. See you next week. Bye.
