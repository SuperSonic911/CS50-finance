# CS50-Finance
![finance](finance.jpg "finance")
### Full stack web application for stock exchange

To use this app you must first obtain an API key from iexcloud

Visit URL: https://iexcloud.io/cloud-login#/register/

Select the “Individual” account type, then enter your name, email address, and a password, and click “Create account”.

Once registered, scroll down to “Get started for free” and click “Select Start plan” to choose the free plan.

Once you’ve confirmed your account via a confirmation email, visit https://iexcloud.io/console/tokens.

Copy the key that appears under the Token column (it should begin with pk_).

In your terminal window, execute:

$ export API_KEY=value

where value is that (pasted) value, without any space immediately before or after the =. You also may wish to paste that value in a text document somewhere, in case you need it again later.

to start the applictation after assigning the API key in the command termianl $flask run


## Different parts of the website:

### Register

Allows a user to register for an account via a form.

### Quote 

 it allows a user to look up a stock’s current price.
 
 ### Buy 
 
 it enables a user to buy stocks
 
 ### index
 
It displays an HTML table summarizing, for the user currently logged in, which stocks the user owns, the numbers of shares owned, the current price of each stock, and the total value of each holding (i.e., shares times price). Also display the user’s current cash balance along with a grand total (i.e., stocks’ total value plus cash)
 
 ### Sell
 
It enables a user to sell shares of a stock (that he or she owns)
 
 ### History
 
It displays an HTML table summarizing all of a user’s transactions ever, listing row by row each and every buy and every sell.
 
 ### Add cash
 
 Allow users to add additional cash to their account.
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
