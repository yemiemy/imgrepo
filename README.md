# ImgRepo -- One location, all your photos...

## An online image repository.

This project provides a platform for people to buy and sell their photo contents. The app was built as a solution to SHopify 2021 challenge.

## Getting Started

There are two levels of access:
1. Buyer account
2. Seller account

Users can decide on which of the two accounts they want to create at signup. They can also upgrade their accounts to a seller account later on.
---

### Buyer's Account
+ As buyers, users can view all image contents on the platform as well as search for images of their choice. 
+ Users can also add images to cart and complete the order anytime they want. They also have the opportunity of buying the images they want at a go.
+ Users have access to their order history. This is where they can view all of the images they have purchased in the past including the ones they have currently in their cart.
+ When users make a purchase and completes payment at the checkout, an email containing all the links to the purchased files (images) will be sent to the users' personal email. This email also acts as sort of an invoice.
+ Users can request for a change of password in situations where they lose their password.
+ Users can decide to monetize their accounts by signing up as a seller on the platform too. To do this, users have to:
    * Go to their dashboard by pressing the "_Hi, User_" button on the navigation bar.
    * Then at the bottom right of the table of items on their dashboard, they can press a button that says "_Become a Seller_".
    * A modal form will pop up. After filling this form, they will be rediredted to their newly updated profile as a seller.

### Seller's Account
+ As sellers, users have the provilege of doing everything in the "_Buyer's Account_" as well as making purchase from other sellers on the platform. 
+ Sellers can upload new photos by following the steps below:
    * Go the dashboard pressing the "_Hi, User_" button on the navigation bar.
    * At the bottom right of the table of items on the dashboard, press a button that says "_Upload Photo_".
    * This will bring up a form. This form entails all the details to be provided for the photo.
      The details include:
        - **name**: This is the name given to the image.
        - **image**: This is the display image which eveyone on the platform can view.
        - **price**: This is the price of the image in USD.
        - **discount_price**: This is field is optional and only needed if there's a cheaper price thatn the original price as discount.
        - **category**: This is the category that best describes the image.
        - **description**: This is a few texts describing what the image is about.
        - **downloadable_file**: This is the orignal image in a zipped folder that the customer can download after making payments for it.
        - **dimension**: This is a specification of the dimenions of the image file.
        - **format**: This is a specification of the file format of the image.
+ Sellers also have the privilege of updating or deleting their own images but do not have the privilege to alter other sellers' images.
+ Sellers can view their earnings based on how many of their images have been downloaded.
+ Sellers can make a request for their payouts. Payouts are made successful if they above a certain threshold of $100.


## Cheers!
You can visit the application at [ImgRepo](http://rasholayemi.pythonanywhere.com/)
There you go. Sign up, decide which account is best for you and get the most out of the platform. Cheers!


**Note** paystack api is used on the backend to handle payments and creation of customer ID.
