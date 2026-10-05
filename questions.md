Q1. Assume you need to support a new command in your program. What would you have to change in your implementation? Is there any way you could avoid changing too much code?
> I add a new case in the match case


Q2. Ticket prices and pricing policies may change during the year, even beyond a simple change of the price table. For example, there could be complex features such as birthday discounts or time-dependent fares. How would you make sure that pricing policies do not affect too much of your code?
> I have a couple of function to calculate the fare, loggin the birthday and addint it to the function would suffice


Q3. You want to get a rough idea of what is expensive (time) in your implementation. How would you do it?
> Spam prints ant time.now, could theorically use a firechart but I nrever used them


Q4. The error messages must be translated to Italian and Neapolitan. In how many places do you have to change your code? How would you bring that number down?
> a bit too many, basically most function return and couple of places in main, I would probably add a dict for the trsnalations and reference it


