def slip1():
    print(""" 
            Q. 1) Write a PHP script to keep track of number of 琀椀mes the web page has been accessed (Use Session
Tracking).
Ans:
<?php
Session_start();
If(isset($_SESSION[‘pcount])) {
$_SESSION[‘pcount] += 1;
} else {
$_SESSION[‘pcount] = 1;
}
Echo “You have visited this page “.$_SESSION[‘pcount].” Time(s).”;
?>
Q. 2)Create ‘Posi琀椀on_Salaries’ Data set. Build a linear regression model by iden琀椀fying independent and
Target variable. Split the variables into training and tes琀椀ng sets. Then divide the training and tes琀椀ng sets
Into a 7:3 ra琀椀o, respec琀椀vely and print them. Build a simple linear regression model.
Ans:
Import numpy as np
Import pandas as pd
From sklearn.model_selec琀椀on import train_test_split   
From sklearn.linear_model import LinearRegression
# Create the Posi琀椀on_Salaries dataset
Data = {‘Posi琀椀on’: [‘CEO’, ‘charman’, ‘director’, ‘Senior Manager’, ‘Junior Manager’, ‘Intern’],
‘Level’: [1, 2, 3, 4, 5, 6],
‘Salary’: [50000, 80000, 110000, 150000, 200000, 250000]}
Df = pd.DataFrame(data)
# Iden琀椀fy the independent and target variables
X = df.iloc[:, 1:2].values
Y = df.iloc[:, 2].values
# Split the variables into training and tes琀椀ng sets with a 7:3 ra琀椀o
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)
# Print the training and tes琀椀ng sets
Print(“X_train:\n”, X_train)
Print(“y_train:\n”, y_train)
Print(“X_test:\n”, X_test)
Print(“y_test:\n”, y_test)
# Build a simple linear regression model
Regressor = LinearRegression()
Regressor.昀椀t(X_train, y_train)
# Print the coe昀케cients and intercept
Print(“Coe昀케cients:”, regressor.coef_)
Print(“Intercept:”, regressor.intercept_)
    
    
    
    """)