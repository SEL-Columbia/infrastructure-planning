# Notes

## Architectural decisions

### Should variations of a tool be combined into a super tool with multiple paths?

No, it is preferable to keep variations of a tool as separate tools, in order to minimize the complexity of any one tool.

For example, if we have multiple ways to estimate electricity demand, then each way should be a separate tool.

### What if the user does not know which tool variation to pick?

We can create a wizard that asks questions and recommends the appropriate tool.

### For sequences of computations, should we require the user to run multiple tools one after the other or should one tool handle the entire sequence?

For convenience and flexibility, we should make both options available. This means that it should be possible to take the results from one tool and feed it into another (for example, if the user wants to use a different population forecasting model than the default provided). It should also be possible to run the entire sequence from start to finish using one tool.

For example, suppose we have a computation sequence that first forecasts population count and then forecasts electricity demand. There should be three tools:

1. Use current population to forecast population count.
2. Use current population to forecast electricity demand.
3. Use future population to forecast electricity demand (if the user wants to specify future population values). It is also possible that case 2 covers case 3 if the user provides future population values. The advantage of having a separate case 3 is that the interface would have fewer parameters and be less cluttered.

If one super tool handles the entire sequence, but there are multiple variations of each sub tool, the user might want to be able to specify different sub tools than those specified by default. The complication here is that a different sub tool might have different parameters.

### How can we have both the convenience of a super tool and the flexibility of different sub tools?

I need to think about this.
