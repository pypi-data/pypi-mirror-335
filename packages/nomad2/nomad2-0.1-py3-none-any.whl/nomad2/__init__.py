def program():
    print("""
    DSA
    1. matrix
    2. singly
    3. doubly
    4. circular
    5. stack
    6. conversion
    7. queue
    8. cirque
    9. sequential
    10. merge
    11. traversal
    12. spanning
    OOP
    1. complex
    2. array
    3. calculator
    4. database
    5. rational
    6. publication
    7. file
    8. temperature
    9. inheritance
    10. vector
    11. string
    12. database1
    13. database2
    14. publication1
""")

def matrix():
    print("""
#include<iostream>
using namespace std;
class matrix
{
	public: int m1[10][10],m2[20][20];
	int r,c,i,j,t;
	void read()
	{
		t=0;
		cout<<"enter the no of rows:"<<endl;
		cin>>r;
		cout<<"enter the no of columns:"<<endl;
		cin>>c;
		cout<<"enter elements of matrix:"<<endl;
		for(i=0;i<r;i++)
		{
			for(j=0;j<c;j++)
			{
				cin>>m1[i][j];
				if(m1[i][j])
				{
					t++;
					m2[t][0]=i+1;
					m2[t][1]=j+1;
					m2[t][2]=m1[i][j];
				}
			}
		}
		m2[0][0]=r;
		m2[0][1]=c;
		m2[0][2]=t;	
	}
	void display()
	{
        cout<<"matrix is:"<<endl;
        for( int i=0;i<r;i++)
        {
            for(j=0;j<c;j++)
            {
                cout<<m1[i][j];
            }
            cout<<"\n";
        }
	}
	void triplet()
	{
		cout<<"sparse matrix triplet is:\n";
		for(i=0;i<=t;i++)
		{
			for(j=0;j<3;j++)
			{
				cout<<m2[i][j]<<" ";
			}
			cout<<"\n";
		
		}
	}
	void transpose()
	{
		int trans[10][5];
		trans[0][0]=m2[0][1];
		trans[0][1]=m2[0][0];
		trans[0][2]=m2[0][2];
		
		int q=1;
		for(i=0;i<=c;i++)
		{
			for(int p=1;p<=t;p++)
			{
				if(m2[p][1]==i)
				{
					trans[q][0]=m2[p][1];
					trans[q][1]=m2[p][0];
					trans[q][2]=m2[p][2];
					q++;
				}
			}
		}
		cout<<"transpose"<<endl;
		for(i=0;i<=t;i++)
		{
			for(j=0;j<3;j++)
			{
				cout<<trans[i][j]<<" ";
			}
			cout<<endl;
		}
	}	
};
int main()
{
	matrix m;
	m.read();
	m.display();
	m.triplet();
	m.transpose();
	return 0;
}
    """)
def singly():
    print("""
#include<iostream> 
using namespace std; 
struct node 
{ 
    int data; 
    struct node*next; 
}; 
node*head=NULL; 
class singly 
{ 
    public: 
    void insertbeg() 
    { 
        cout<<"Enter the Data:"<<"\n"; 
        node*nn=new node; 
        if(head==NULL) 
        { 
            cin>>nn->data; 
            nn->next=NULL; 
            head=nn; 
        } 
        else 
        { 
            cin>>nn->data; 
            nn->next=head; 
            head=nn; 
        } 
    } 
    void display() 
    { 
        node*temp=head; 
        while(temp!=NULL) 
        { 
            cout<<temp->data<<"->"; 
            temp=temp->next; 
        } 
        cout<<"NULL"<<endl; 
    } 
    void insertend() 
    { 
        node*temp=head; 
        cout<<"Enter the Data:"<<"\n"; 
        node*nn=new node; 
        nn->next=NULL; 
        if(head==NULL) 
        { 
            cin>>nn->data; 
            nn->next=NULL; 
            head=nn; 
        } 
        else 
        { 
            while(temp->next!=NULL) 
            { 
                temp=temp->next; 
            } 
            cin>>nn->data; 
            temp->next=nn; 
        } 
    } 

    void insertran() 
    { 
        int loc; 
        node*nn=new node; 
        nn->next=NULL; 
        cout<<"Enter the Location :"<<endl; 
        cin>>loc; 
        cout<<"Enter the data:"<<endl; 
        if(loc<1) 
        { 
            cout<<"Location should be greater than 1:"<<"\n"; 
        } 
        else if(loc==1) 
        { 
            cin>>nn->data; 
            nn->next=head; 
            head=nn; 
        } 
        else 
        { 
            node *temp=head; 
            for(int i=1;i<loc-1;i++) 
            { 
                if(temp!=NULL) 
                { 
                    temp=temp->next; 
                } 
            } 
            if(temp!=NULL) 
            { 
                cin>>nn->data; 
                nn->next=temp->next; 
                temp->next=nn; 
            } 
            else 
            { 
                cout<<"the previous node is null"<<"\n"; 
            } 
        } 
    } 
    void deletebin() 
    { 
        node *temp; 
        if(head==NULL) 
        { 
            cout<<"Underflow Plz First insert a node first\n"<<endl; 
        } 
        else 
        { 
            temp=head; 
            head=head->next; 
            delete temp; 
        } 
    } 
    void deleteend() 
    { 
        node *temp; 
        node *current; 
        if(head==NULL) 
        { 
            cout<<"Underflow Plz First insert a node first\n"<<endl; 
        } 
        else 
        { 
            temp=head; 
            while(temp->next!=NULL) 
            { 
                current=temp; 
                temp=temp->next; 
            } 
            current->next=NULL; 
            delete temp; 
        } 
    } 
    void deleteran() 
    { 
        if(head==NULL) 
        { 
            cout<<"List is Empty please Insert a Node First\n"<<endl; 
        } 
        else 
        { 
            int pos,i=1; 
            node *temp,*nextnode; 
            cout<<"Plz enter Position : "; 
            cin>>pos; 
            temp=head; 
            while(i<pos-1) 
            { 
                temp=temp->next; 
                i++; 
            } 
            nextnode=temp->next; 
            temp->next=nextnode->next; 
            delete nextnode; 
        } 
    } 
}; 
int main() 
{ 
    Linked L1; 
    int ch; 
    while(1) 
    { 
        cout<<"---menu---"<<"\n"; 
        cout<<"1.Insert at Begin"<<"\n"; 
        cout<<"2.Insert at End"<<"\n"; 
        cout<<"3.Insert at random "<<"\n"; 
        cout<<"4.Delete at Begin"<<"\n"; 
        cout<<"5.Delete at End"<<"\n"; 
        cout<<"6.Delete at Random Position\n"; 
        cout<<"7.Exit"<<"\n"; 
        cout<<"Enter choice :";
        cin>>ch; 
        switch(ch) 
        { 
            case 1: 
                L1.insertbeg(); 
                L1.display(); 
                break; 
            case 2: 
                L1.insertend(); 
                L1.display(); 
                break; 
            case 3: 
                L1.insertran(); 
                L1.display(); 
                break; 
            case 4: 
                L1.deletebin(); 
                L1.display(); 
                break; 
            case 5: 
                L1.deleteend(); 
                L1.display(); 
                break; 
            case 6: 
                L1.deleteran(); 
                L1.display(); 
                break; 
            case 7: 
                exit(0); 
                cout<<"Thank You!"; 
        } 
    } 
} 
    """)
def doubly():
    print("""
#include <iostream>
using namespace std;
struct node
{
    int data;
    node* next;
    node* prev;
};
node *head=NULL;
class doubly
{
    public:
    void insertbeg()
    {
        cout<<"Enter the data :"<<endl;
        node *nn=new node;
        nn->next=head;
        nn->prev=NULL;
        if(head==NULL)
        {
            cin>>nn->data;
            head=nn;
        }
        else
        {
            cin>>nn->data;
            head->prev=nn;
            head=nn;
        }
    }
    void displaybeg()
    {
        node *temp=head;
        while (temp!=NULL)
        {
            cout<<temp->data<<"<=>";
            temp=temp->next;
        }
        cout<<"NULL"<<endl;
    }
    void insertend()
    {
        cout<<"Enter the data :"<<endl;
        node *nn=new node;
        nn->next=NULL;
        nn->prev=NULL;
        if(head==NULL)
        {
            cin>>nn->data;
            head=nn;
        }
        else
        {
            cin>>nn->data;
            node *temp=head;
            while(temp->next!=NULL)
            {
                temp=temp->next;
            }
            temp->next=nn;
            nn->prev=temp;
        }
    }

    void displayend()
    {
        node *temp=head;
        while (temp!=NULL)
        {
            cout<<temp->data<<"<=>";
            temp=temp->next;
        }
        cout<<"NULL"<<endl;
    }
    void insertloc()
    {
        int loc;
        node *nn=new node;
        nn->next=NULL;
        nn->prev=NULL;
        cout<<"Enter the Location :"<<endl;
        cin>>loc;
        cout<<"Enter the data :"<<endl;
        if(loc<1)
        {
            cout<<"Location should be greater than 1.\n";
        }
        else if(loc==1)
        {
            cin>>nn->data;
            nn->next=head;
            head->prev=nn;
            head=nn;
        }
        else
        {
            node *temp=head;
            for(int i=1; i<loc-1; i++)
            {
                if(temp!=NULL)
                {
                    temp=temp->next;
                }
            }
            if(temp!=NULL)
            {
                cin>>nn->data;
                nn->next=temp->next;
                nn->prev=temp;
                temp->next=nn;
            }
            if(nn->next!=NULL)
            {
                nn->next->prev=nn;
            }
            else
            {
                cout<<"The previous node is null.\n";
            }
        }
    }
    void displayloc()
    {
        node *temp=head;
        while (temp!=NULL)
        {
            cout<<temp->data<<"<=>";
            temp=temp->next;
        }
        cout<<"NULL"<<endl;
    }
    void deletebeg()
    {
        node *temp;
        if(head==NULL)
        {
            cout<<"Please insert a node first..!";
        }
        else
        {
            temp=head;
            head=head->next;
            delete temp;
        }
        if(head!=NULL)
        {
            head->prev=NULL;
        }
    }
    void deleteend()
    {
        node *temp;
        node *curr;
        if(head!=NULL)
        {
            if(head->next==NULL)
            {
                head=NULL;
            }
            else
            {
                temp=head;
                while(temp->next->next!=NULL)
                {
                    temp=temp->next;
                }
                curr=temp->next;
                temp->next=NULL;
                delete curr;
            }
        }
    }
    void deleteloc()
    {
        int pos;
        cout<<"Enter the Position :"<<endl;
        cin>>pos;
        if(pos < 1)
        {
            cout<<"\nPosition should be >= 1."<<endl;
        }
        else if (pos == 1 && head != NULL)
        {
            node *del_node = head;
            head = head->next;
            delete del_node;
            if(head != NULL)
            {
                head->prev = NULL;
            }
        }
        else
        {
            node *temp = head;
            for(int i = 1; i < pos-1; i++)
            {
                if(temp != NULL)
                {
                    temp = temp->next;
                }
            }
            if(temp != NULL && temp->next != NULL)
            {
                node *del_node = temp->next;
                temp->next = temp->next->next;
                if(temp->next->next != NULL)
                {
                    temp->next->next->prev = temp->next;
                }
                delete del_node;
            }
            else
            {
                cout<<"\nThe node is already null."<<endl;
            }
        }
    }
};


int main()
{
    doubly obj;
    int ch;
    while(1)
    {
        cout<<"1.Insert | 2.Delete | 3.Exit"<<endl;
        cout<<"Enter the choice : ";
        cin>>ch;
        switch (ch)
        {
            case 1: int b;
                cout<<"1.Insert at Beginning|2.Insert at Specific Location|3.Insert at End "<<endl;
                cout<<"Enter the choice : ";
                cin>>b;
                switch(b)
                {
                    case 1: 
                        obj.insertbeg();
                        obj.displaybeg();
                        break;
                    case 2: 
                        obj.insertloc();
                        obj.displayloc();
                        break;
                    case 3: 
                        obj.insertend();
                        obj.displayend();
                        break;
                }
                break;
            case 2: 
                int d;
                cout<<"1.Delete at Beginning|2.Delete at Specific Location|3.Delete at End "<<endl;
                cout<<"Enter the choice : ";
                cin>>d;
                switch(d)
                {
                    case 1: 
                        obj.deletebeg();
                        obj.displaybeg();
                        break;
                    case 2: 
                        obj.deleteloc();
                        obj.displayloc();
                        break;
                    case 3: 
                        obj.deleteend();
                        obj.displayend();
                        break;
                }
                break;
            case 3:
                cout<<"THANK YOU!"<<endl;
                exit(0);
        }
    }
    return 0;
}
	""")
def circular():
    print("""
#include<iostream> 
using namespace std; 

struct node 
{ 
int data; 
node *next; 
}; 
node *head=NULL; 

class circular 
{ 
public: 
//Insert at the END 
void insertend() 
{ 
cout<<"Enter the data :"<<endl; 
node *nn=new node; 
nn->next=NULL; 
if(head==NULL) 
{ 
cin>>nn->data; 
head=nn; 
nn->next=head; 
} 
else 
{ 
cin>>nn->data; 
node *temp=head; 
while (temp->next!=head) 
{ 
temp=temp->next; 
} 
temp->next=nn; 
nn->next=head; 
} 
} 
//Insert at the Specific Location 
void insertloc() 
{ 
int loc; 
node *nn=new node; 
nn->next=NULL; 
node *temp=head; 
cout<<"Enter the Location :"<<endl; 
cin>>loc; 
cout<<"Enter the data :"<<endl; 
if(loc<1) 
{ 
cout<<"Location should be greater than 1.\n"; 
} 
else if(loc==1) 
{ 
if(head==NULL) 
{ 
cin>>nn->data; 
nn->next=head; 
head=nn; 
} 
else 
{ 
while (temp->next!=head) 
{ 
temp=temp->next; 
} 
nn->next=head; 
head=nn; 
temp->next=nn; 
} 
} 
else 
{ 
temp=head; 
for(int i=1; i<loc-1; i++) 
{ 
if(temp!=NULL) 
{ 
temp=temp->next; 
} 
} 
cin>>nn->data; 
nn->next=temp->next; 
temp->next=nn; 
} 
} 
//Insert at the Beginning 
void insertbeg() 
{ 
cout<<"Enter the data :"<<endl; 
node *nn=new node; 
nn->next=NULL; 
if(head==NULL) 

{ 
cin>>nn->data; 
head=nn; 
nn->next=head; 
} 
else 
{ 
cin>>nn->data; 
node *temp=head; 
while (temp->next!=head) 
{ 
temp=temp->next; 
} 
temp->next=nn; 
nn->next=head; 
head=nn; 
} 
} 

void deletebin() 
{ 
if(head==NULL) 
{ 
cout<<"List is Empty please Insert a Node First\n"<<endl; 
} 
if(head!=NULL) 
{ 
if(head->next==head) 
{ 
head=NULL; 
} 
else 
{ 
node *temp=head; 
node *fn=head; 
while(temp->next!=head) 
{ 
temp=temp->next; 
} 
head=head->next; 
temp->next=head; 
delete fn; 
} 
} 
} 
void deleteend() 
{ 
if(head==NULL) 
{ 
cout<<"List is Empty please Insert a Node First\n"<<endl; 
} 
if(head!=NULL) 
{ 
if(head->next==head) 
{ 
head=NULL; 
} 
else 
{ 
node *temp=head; 
while(temp->next->next!=head) 
{ 
temp=temp->next; 
} 
node *ln=temp->next; 
temp->next=head; 
delete ln; 
} 
} 
} 
void deleteran() 
{ 
node *temp=head; 
node *del_node=head; 
int pos; 
cout<<"Enter the Position :"<<endl; 
cin>>pos; 
if(pos < 1) 
{ 
cout<<"\nPosition should be >= 1."<<endl; 
} 
else if (pos == 1) 
{ 
if(head->next==head) 
{ 
head=NULL; 
} 
else 
{ 
while(temp->next->next!=head) 
{ 
temp=temp->next; 
} 
head=head->next; 
temp->next=head; 
delete del_node; 
} 
} 
else 
{ 
temp=head; 
for(int i=1; i<pos-1; i++) 
{ 
temp=temp->next; 
} 
del_node=temp->next; 
temp->next=temp->next->next; 
delete del_node; 
} 
} 
void display() 
{ 
node *temp=head; 
if(temp!=NULL) 
{ 
cout<<"Start"; 
while (1) 
{ 
cout<<"->"<<temp->data; 
temp=temp->next; 
if(temp==head) 
break; 
} 
cout<<"->"<<endl; 
} 
} 
}; 
int main() 
{ 
circular cir; 
int ch; 
while(1) 
{ 
cout<<"1.Insert | 2. Delete | 3.Exit"<<endl; 
cout<<"Enter the choice : "; 
cin>>ch; 
switch (ch) 
{ 
case 1: int b; 
cout<<"1.Insert at Beginning|2.Insert at Specific Location|3.Insert at End "<<endl; 
cout<<"Enter the choice : "; 
cin>>b; 
switch(b) 
{ 
case 1: cir.insertbeg(); 
cir.display(); 
break; 
case 2: cir.insertloc(); 
cir.display(); 
break; 
case 3: cir.insertend(); 
cir.display(); 
break; 
} 
break; 
case 2: int d; 
cout<<"1.Delete at Beginning|2.Delete at Specific Location|3.Delete at End "<<endl; 
cout<<"Enter the choice : "; 
cin>>d; 
switch(d) 
{ 
case 1: cir.deletebin(); 
cir.display(); 
break; 
case 2: cir.deleteran(); 
cir.display(); 
break; 
case 3: cir.deleteend(); 
cir.display(); 
break;  
} 
break; 
case 3: exit(0); 
} 
} 
return 0; 
} 
    """)
def stack():
    print("""
#include<iostream>
using namespace std;
class STACK{
	public:
	int top=-1;
	int max[4];
	int size=4;
    void push()
	{	
	    int no;
		if(top==size-1)
		{
		cout<<"stack is overflow"<<endl;
		}
	    else
		{
	    top++;
		cout<<"enter the elements:"<<endl;
		cin>>no;
		max[top]=no;
		cout<<"inserted:"<<no<<endl;
		}
	}			
			void pop()
			{
				if((max[top])==-1)
				{
					cout<<"stack is underflow"<<endl;
				}
				else
				{	
					cout<<"pop element"<<max[top]<<endl;
					top--;
				}
			}			
			void display()
			{
				if(max[top]==-1)
				{
					cout<<"stack is empty\n";
				}
				else
				{				
					for(int i=top;i>=0;i--)
					{
						cout<<max[i]<<endl;
					}
				}
			}				
};
int main()
{	
 	STACK s1;
 	int ch,no;	
 	do{
 	cout<<"*****DISPLAY MENU****"<<endl;
 	cout<<"1.push"<<endl;
 	cout<<"2.pop"<<endl;
 	cout<<"3.display"<<endl;
 	cout<<"4.Exit"<<endl;	
 		cout<<"enter your choices:"<<endl;
 		cin>>ch;
 		switch(ch)
 		{
 			case 1:				
				s1.push();
				s1.display();
				break;
			case 2: 
				s1.pop();				
				break;							
			case 3:
				s1.display();
				break;							
			case 4:
				cout<<"Exit"<<endl;
				break;																
 		}
 	}while(ch!=4);
 	return 0;
}
    """)
def queue():
    print("""
#include<iostream>
using namespace std;
#define size 3
class Queue
{
	public:int Q[size],no,rear=-1, front=-1;		
	 void Enqueue()
	{			
		cout<<"enter value to insert"<<endl;
		cin>>no;		
		if(rear==size-1)
		{
			cout<<"queue is full"<<endl;
		}
		else if(rear==-1 && front==-1)
			{
			rear++;
			front++;
			Q[rear]=no;
			}
			else
			{
				rear++;
				Q[rear]=no;
			}
	}		
	void Dequeue()
	{	
		if(rear==-1 && front==-1)
		{
			cout<<"queue is empty"<<endl;
		}
		else if(front==rear)
		{	
			cout<<"delete element is:"<<Q[front]<<endl;
			front=-1;
			rear=-1;
		}
		else
		{	
			cout<<"---delete ele is:"<<Q[front]<<endl;
			front++;			
		}
	}
	void Display()
	{		
		if(rear==-1 && front==-1)
		{
			cout<<"queue is empty"<<endl;
		}
		else
		{	
			cout<<"element in queue is:"<<endl;
			for(int i=front;i<=rear;i++)
			{
				cout<<Q[i]<<endl;
			}
		}
	}
};
int main()
{	
 	Queue q1;
 	int ch,no; 	
 	do{
 	cout<<"*****DISPLAY MENU****"<<endl;
 	cout<<"1.Enqueue"<<endl;
 	cout<<"2.Dequeue"<<endl;
 	cout<<"3.Display"<<endl;
 	cout<<"4.Exit"<<endl; 	
 		cout<<"enter your choices:"<<endl;
 		cin>>ch;
 		switch(ch)
 		{
 			case 1:				
				q1.Enqueue();
				break;			
			case 2: 
				q1.Dequeue();				
				break;							
			case 3:
				q1.Display();
				break;							
			case 4:
				cout<<"Exit"<<endl;
				break;									
 		}
 	}while(ch!=4);
 	return 0;
}   
""")  
def conversion():
    print("""
#include<bits/stdc++.h>
using namespace std;
int prec(char ch)
{
	if(ch=='^')
		return 3;
	else if(ch=='/'||ch=='*')
		return 2;
	else if(ch=='+'||ch=='-')
		return 1;
	else 
		return -1;
}
string infixTopostfix(string s)
{
	stack<char> st;
	string ans = "";
	for(int i=0;i<s.length();i++)
	{
		char ch = s[i];
		if((ch>='a' && ch<='z')||(ch>='A' && ch<='Z')||(ch>='0' && ch<='9'))
			ans+=ch;
		else if(ch=='(')
			st.push('(');
		else if(ch==')')
		{
			while(st.top()!='(')
			{
				ans+=st.top();
				st.pop();
			}
			st.pop();
		}
		else
		{
			while(!st.empty() && prec(s[i])<=prec(st.top()))
			{
				ans+=st.top();
				st.pop();
			}
			st.push(ch);
		}
	}
	while(!st.empty())
	{
		ans+=st.top();
		st.pop();
	}
	return ans;
}
int main()
{
	string s;
	cin>>s;
	cout<<infixTopostfix(s);
	return 0;
}
""")
def cirque():
    print("""
#include<iostream>
using namespace std;

#define size 4
class cirque
{
	public:int Q[size],no,rear=-1, front=-1;				
	 void Enqueue()
	{		
		cout<<"enter value to insert"<<endl;
		cin>>no;		
		if((rear==size-1 && front==0))
		{
			cout<<"queue is full"<<endl;
		}
		else if(rear==-1 && front==-1)		
			{			
			rear++;
			front++;
			Q[rear]=no;
			}
			else //if(rear==size-1 && front!=0)
			{
				rear++;
				Q[rear]=no;
			}
	}	
	void Dequeue()
	{		
		if(rear==-1 && front==-1)
		{
			cout<<"queue is empty"<<endl;
		}
		else if(front==rear)
		{	
			cout<<"delete element is:"<<Q[front]<<endl;
			front=-1;
			rear=-1;
		}
		else
		{	
			cout<<"---delete ele is:"<<Q[front]<<endl;
			front++;			
		}
	}		
	void Display()
	{
		
		if(rear==-1 && front==-1)
		{
			cout<<"queue is empty"<<endl;
		}
		else
		{	
			cout<<"element in queue is:"<<endl;
			for(int i=front;i<=rear;i++)
			{
				cout<<Q[i]<<endl;
			}
		}
	}
};
int main()
 {	
 	cirque q1;
 	int ch,no;	
 	do{
 	cout<<"*****DISPLAY MENU****"<<endl;
 	cout<<"1.Enqueue"<<endl;
 	cout<<"2.Dequeue"<<endl;
 	cout<<"3.Display"<<endl;
 	cout<<"4.Exit"<<endl;
 	
 		cout<<"enter your choices:"<<endl;
 		cin>>ch;
 		switch(ch)
 		{
 			case 1: 				
				q1.Enqueue();
				break;							
			case 2: 
				q1.Dequeue();				
				break;							
			case 3:
				q1.Display();
				break;							
			case 4:
				cout<<"Exit"<<endl;
				break;		
 		}
 	}while(ch!=4);
 	return 0;
 }
""")
def sequential():
    print("""
#include <iostream>
using namespace std;
int main() {
    int arr[10],n,key;
    cout<<"Enter array size :";
    cin>>n;
    cout<<"Enter elements :";
    for (int i = 0; i < n; i++) 
    {
        cin>>arr[i];
    }
    cout<<"Enter key to search :";
    cin>>key;
    for (int i = 0; i < n; i++) 
    {
        if (arr[i] == key) 
        {
            cout << "Element is present at index " << i << endl;
            return 0;
        }
    }
    cout << "Element is not present in array" << endl;      
    return 0;
}
""")   
def merge():
    print("""
#include <iostream>
using namespace std;
void merge(int arr[], int left, int mid, int right) {
    int n1 = mid - left + 1;
    int n2 = right - mid;
    int L[n1], R[n2];
    for (int i = 0; i < n1; i++)
        L[i] = arr[left + i];
    for (int j = 0; j < n2; j++)
        R[j] = arr[mid + 1 + j];
    int i = 0, j = 0, k = left;
    while (i < n1 && j < n2) {
        if (L[i] <= R[j]) {
            arr[k] = L[i];
            i++;
        } else {
            arr[k] = R[j];
            j++;
        }
        k++;
    }
    while (i < n1) {
        arr[k] = L[i];
        i++;
        k++;
    }
    while (j < n2) {
        arr[k] = R[j];
        j++;
        k++;
    }
}
void mergeSort(int arr[], int left, int right) {
    if (left < right) {
        int mid = left + (right - left) / 2;
        mergeSort(arr, left, mid);
        mergeSort(arr, mid + 1, right);
        merge(arr, left, mid, right);
    }
}
void printArray(int A[], int size) {
    for (int i = 0; i < size; i++)
        cout << A[i] << " ";
}
int main() {
    int arr[] = {12, 11, 13, 5, 6, 7};
    int arr_size = sizeof(arr) / sizeof(arr[0]);
    cout << "Given array is \n";
    printArray(arr, arr_size);
    mergeSort(arr, 0, arr_size - 1);
    cout << "\nSorted array is \n";
    printArray(arr, arr_size);
    return 0;
}
""") 
def traversal():
    print("""
#include <iostream>
using namespace std;
struct Node {
    int data;
    Node *left, *right;
};
Node* newNode(int data) {
    Node* node = new Node;
    node->data = data;
    node->left = node->right = NULL;
    return node;
}
void inorderTraversal(Node* root) {
    if (root == NULL)
        return;
    inorderTraversal(root->left);
    cout << root->data << " ";
    inorderTraversal(root->right);
}
void preorderTraversal(Node* root) {
    if (root == NULL)
        return;
    cout << root->data << " ";
    preorderTraversal(root->left);
    preorderTraversal(root->right);
}
void postorderTraversal(Node* root) {
    if (root == NULL)
        return;
    postorderTraversal(root->left);
    postorderTraversal(root->right);
    cout << root->data << " ";
}
int main() {
    Node* root = newNode(1);
    root->left = newNode(2);
    root->right = newNode(3);
    root->left->left = newNode(4);
    root->left->right = newNode(5);
    cout << "Inorder Traversal: ";
    inorderTraversal(root);
    cout << endl;
    cout << "Preorder Traversal: ";
    preorderTraversal(root);
    cout << endl;
    cout << "Postorder Traversal: ";
    postorderTraversal(root);
    cout << endl;
    return 0;
}
""")
def spanning():
    print("""
#include <cstring>
#include <iostream>
using namespace std;
#define INF 9999999
#define V 5
int G[V][V] = {
  {0, 9, 75, 0, 0},
  {9, 0, 95, 19, 42},
  {75, 95, 0, 51, 66},
  {0, 19, 51, 0, 31},
  {0, 42, 66, 31, 0}};
int main() {
  int no_edge;
  int selected[V];
  memset(selected, false, sizeof(selected));
  no_edge = 0;
  selected[0] = true;
  int x;
  int y; 
  cout << "Edge"
     << " : "
     << "Weight";
  cout << endl;
  while (no_edge < V - 1) {
    int min = INF;
    x = 0;
    y = 0;
    for (int i = 0; i < V; i++) {
      if (selected[i]) {
        for (int j = 0; j < V; j++) {
          if (!selected[j] && G[i][j]) {  // not in selected and there is an edge
            if (min > G[i][j]) {
              min = G[i][j];
              x = i;
              y = j;
            }
          }
        }
      }
    }
    cout << x << " - " << y << " :  " << G[x][y];
    cout << endl;
    selected[y] = true;
    no_edge++;
  }
  return 0;
}
""")
def complex():
    print("""
#include<iostream>
using namespace std;
class Complex
{
	private:
	int real, img;
	
	public:
	Complex(int re = 0,int im = 0)
	{
		real = re;
		img = im;
	}
	Complex operator +(Complex const &obj)
	{
		Complex temp;
		temp.real=real+obj.real;
		temp.img=img+obj.img;
		return(temp);
	}
	Complex operator *(Complex &obj)
	{
		Complex temp1;
		temp1.real=(real*obj.real)-(img*obj.img);
		temp1.img=(img*obj.real)+(real*obj.img);
		return(temp1);
	}
	void display()
	{
		cout<<real<<"+"<<img<<"i"<<endl;
	}
};
int main()
{
	Complex c1(9,5),c2(4,3);
	Complex c3=c1+c2;
	c3.display();
	Complex c4=c1*c2;
	c4.display();
	return 0;
}
""")
def array():
    print("""
#include <iostream>
using namespace std;

class array
{
	public:
		int arr[10], arr1[10], n=4;
		void create() 
		{
		    cout << "Enter elements for the array:\n";
		    for (int i = 0; i < n; i++) 
		    {
			cin >> arr[i];
		    }
		}

		void display() 
		{
		    cout << "Elements of the array:\n";
		    for (int i = 0; i < n; i++) 
		    {
			cout << arr[i] << " ";
		    }
		    cout << endl;
		}
		void copy()
		{
			int arr1[10];
			for (int i = 0; i < n; i++) 
		    	{
				arr1[i] = arr[i];
		    	}
		    	cout << "Elements of the copied array:\n";
		    	for (int i = 0; i < n; i++) 
		    	{
				cout << arr1[i] << " ";
			}
			cout << endl;
		}
		void sizecheck()
		{
			cout << "Size of array\n";
			cout << n ;
		}
		void range()
		{
			cout << "Range of array is :" << arr[n-1] << " to " << arr[0];
		}
		void equal()
		{	
			bool b = 1;
			for (int i = 0; i < n; i++) 
		    	{
				if(arr[i] == arr1[i])
				{
					b = 0;
				}
			}
			if(b == 1)
				cout << "Both array are equal";
			else
				cout << "Both array are not equal";

		}
};

int main()
{
	array arra;
	int ch;
	
	do 
	{
		cout << "\n***********Menu************";
		cout << "\n1. Create Array:";
		cout << "\n2. Display Array:";
		cout << "\n3. Copy Array:";
		cout << "\n4. Size of Array:";
		cout << "\n5. Range :";
		cout << "\n6. Equality Check";
		cout << "\n7. Exit";
		cout << "\nEnter your choice: ";
		cin >> ch;

		switch (ch) 
		{
		    case 1:
		        arra.create();
		        break;
		    case 2:
		      	arra.display();
		        break;
		    case 3:
		      	arra.copy();
		        break;
		    case 4:
		      	arra.sizecheck();
		        break;
		    case 5:
		      	arra.range();
		        break;
		    case 6:
		      	arra.equal();
		        break;
		    case 7:
		        cout << "Exit\n";
		        break;
		}
    } while (ch != 7);

    return 0;
}
""")
def calculator():
    print("""#include <iostream>
using namespace std;

class cal {
public:
    void add() 
    {
        int n1, n2;
        cout << "Enter first number: ";
        cin >> n1;
        cout << "Enter second number: ";
        cin >> n2;
        int addi = n1 + n2; 
        cout << "Addition is: " << addi << "\n";
    }

    void sub() 
    {
        int n1, n2;
        cout << "Enter first number: ";
        cin >> n1;
        cout << "Enter second number: ";
        cin >> n2;
        int subs = n1 - n2; 
        cout << "Subtraction is: " << subs << "\n";
    }

    void mul() 
    {
        int n1, n2;
        cout << "Enter first number: ";
        cin >> n1;
        cout << "Enter second number: ";
        cin >> n2;
        int mult = n1 * n2; 
        cout << "Multiplication is: " << mult << "\n";
    }

    void div() 
    {
        int n1, n2;
        cout << "Enter first number: ";
        cin >> n1;
        cout << "Enter second number: ";
        cin >> n2;
        int divi = n1/n2; 
        cout << "Division is: " << divi << "\n";
        
    }
};

int main() 
{
    cal calc;
    int ch;

    do 
    {
        cout << "\n***********Menu************";
        cout << "\n1. Addition";
        cout << "\n2. Subtraction";
        cout << "\n3. Multiplication";
        cout << "\n4. Division";
        cout << "\n5. Exit";
        cout << "\nEnter your choice: ";
        cin >> ch;

        switch (ch) 
        {
            case 1:
                calc.add();
                break;
            case 2:
                calc.sub();
                break;
            case 3:
                calc.mul();
                break;
            case 4:
                calc.div();
                break;
            case 5:
                cout << "Exit\n";
                break;
        }
    } while (ch != 5);

    return 0;
}""")
def database():
    print("""
#include<iostream>
#include<string.h>
using namespace std;
class student
{
   int roll;
   char name[20];
   char Class[5];
   char Div[10];
   char dob[20];
   char bg[5];
   char phone[12];
   char city[10];
   char license[12];
   public:
   static  int stdno;
   static  void count()
   {
      cout<<"Enter the student number",stdno;              
   }    
   student()
   {
      roll=1;
      strcpy(name,"Cherry");
      strcpy(Class,"Fymca");
      strcpy(Div,"A");
      strcpy(dob,"20/11/2002");
      strcpy(bg,"O+");
      strcpy(phone,"9766196688");
      strcpy(city,"Nashik");
      strcpy(license,"Sidd733");
      ++stdno;
   }
   void getData()
   {
      cout<<"\n Enter: Name\tRoll No\tClass\tDiv\tDate of Birth\tBlood group\tPhone\tcity\tLicense:\n";
      cin>>name>>roll>>Class>>Div>>dob>>bg>>phone>>city>>license;
   }
   friend void Display(student d);
   ~student()
   {
      cout<<"Object is deleted....";
   }
};
void Display(student d1)
{
      cout<<"\nName :"<<d1.name;
      cout<<"\nroll no:"<<d1.roll;
      cout<<"\nClass :"<<d1.Class;
      cout<<"\nDiv :"<<d1.Div;
      cout<<"\nDate of birth :"<<d1.dob;
      cout<<"\nBlood Group :"<<d1.bg;
      cout<<"\nPhone NUmber :"<<d1.phone;
      cout<<"\nCity :"<<d1.city<<endl;
      cout<<"\nlicense Number :"<<d1.license;      
}
int student::stdno;
int main()
{
   student d1; 
   Display(d1);  
   d1.getData();
   Display(d1);
   return 0;
}
""")
def rational():
    print("""
#include <iostream>
using namespace std;
class Ral {
    int den, num;
public:
    void set(int d, int n) {
        den = d;
        num = n;
    }
    Ral operator+(Ral R) {
        Ral temp;
        temp.den = den + R.den;
        temp.num = num + R.num;
        return temp;
    }
    Ral operator*(Ral R) {
        Ral temp;
        temp.den = den * R.den;
        temp.num = num * R.num;
        return temp;
    }
    Ral operator-(Ral C) {
        Ral temp;
        temp.den = den - C.den;
        temp.num = num - C.num;
        return temp;
    }
    void show() {
        cout << "a=" << num << endl;
        cout << "b=" << den << endl;
    }
    void Exit() {
        cout << "BYE" << endl; 
    }
};
int main() {
    Ral c1, c2, c3, c4, c5;
    int choice;
    c1.set(5, 10); 
    c2.set(3, 7); 
	do
	{
    cout << "Choose an operation: " << endl;
    cout << "1. Addition" << endl;
    cout << "2. Multiplication" << endl;
    cout << "3. Subtraction" << endl;
    cout << "4. Exit" << endl;
    cin >> choice;
    switch (choice) {
        case 1:
            c3 = c1 + c2;
            cout << "For addition:" << endl;
            c3.show();
            break;
        case 2:
            c4 = c1 * c2;
            cout << "For multiplication:" << endl;
            c4.show();
            break;
        case 3:
            c5 = c1 - c2;
            cout << "For subtraction:" << endl;
            c5.show();
            break;
        case 4:
            c1.Exit();
            break;
        default:
            cout << "Invalid choice!" << endl;
            break;
    }
    }while(choice!=4);
    return 0;
}
""")
def publication():
    print("""
#include<iostream>
using namespace std;
class Publication
{
	public:
	string title;
	float price;
	void get()
	{
		cout<<"Enter title :";
		cin>>title;
		cout<<"Enter price :";
		cin>>price;
	}
	void put()
	{
		cout<<"Title is :"<<title<<endl;
		cout<<"Price is :"<<price<<endl;
	}
};
class Book: public Publication
{
	public:
	int page_no;
	void get2()
	{
		cout<<"Enter no. of pages of book :";
		cin>>page_no;
	}
	void put2()
	{
		cout<<"Number of pages of book :"<<page_no<<endl;
	}	
};
class Tape: public Publication
{
	public:
	float time;
	void get3()
	{
		cout<<"Enter time of tape :";
		cin>>time;
	}
	void put3()
	{
		cout<<"Time of tape :"<<time<<endl;
	}
};
int main()
{
	cout<<"Enter Data :"<<endl;
	Tape t1;
	t1.get();
	t1.get3();
	Book b1;
	b1.get2();
	cout<<endl;
	cout<<"Show Data :"<<endl;
	t1.put();
	t1.put3();
	b1.put2();
	return 0;
}
""")
def file():
    print("""
#include<iostream>
#include<fstream>
using namespace std;
main()
{
    int rno,fee;
    char name[50];
    cout<<"Enter the Roll Number:";
    cin>>rno;
    cout<<"\nEnter the Name:";
    cin>>name;
    cout<<"\nEnter the Fee:";
    cin>>fee;
    ofstream fout("C:/Users/vinit/Desktop/yashjava/OOP/student.txt");
    fout<<rno<<"\t"<<name<<"\t"<<fee;
    fout.close();
    ifstream fin("C:/Users/vinit/Desktop/yashjava/OOP/student.txt");
    fin>>rno>>name>>fee;
    fin.close();
    cout<<endl<<rno<<"\t"<<name<<"\t"<<fee;
    return 0;
}
""")
def temperature():
    print("""
#include <iostream>
class convert {
protected:
    double val1; 
    double val2; 
public:
    convert(double v) : val1(v), val2(0.0) {} 
    double getinit() const { return val1; }
    double getconv() const { return val2; }
    virtual void compute() = 0; 
    virtual ~convert() {} 
};
class CtoF : public convert {
public:
    CtoF(double c) : convert(c) {}

    void compute() override { val2 = (val1 * 9.0 / 5.0) + 32.0; }
};
class KtoM : public convert {
public:
    KtoM(double k) : convert(k) {}

    void compute() override { val2 = val1 * 0.621371; }
};
int main() {
    CtoF c_to_f(25.0);
    c_to_f.compute();
    std::cout << c_to_f.getinit() << " Celsius is equal to " << c_to_f.getconv() << " Fahrenheit" << std::endl;
    KtoM k_to_m(100.0);
    k_to_m.compute();
    std::cout << k_to_m.getinit() << " Kilometers is equal to " << k_to_m.getconv() << " Miles" << std::endl;         
    convert* converter;
    converter = new CtoF(0.0);
    converter->compute();
    std::cout << converter->getinit() << " Celsius is equal to " << converter->getconv() << " Fahrenheit" << std::endl;
    delete converter;
    converter = new KtoM(160.934);
    converter->compute();
    std::cout << converter->getinit() << " Kilometers is equal to " << converter->getconv() << " Miles" << std::endl;
    delete converter;
    return 0;
}
""")
def inheritance():
    print("""
#include<iostream>
using namespace std;
//single level inheritance
class geometric
{
	public:
		int l,b;
		void read()
		{
			cout<<"Enter length of rectangle :\n";
			cin>>l;
			cout<<"Enter breadth of rectangle :\n";
			cin>>b;
		}
};
class rectangle: public geometric
{
	public:
		int ar;
		void area()
		{
			cout<<"Area of rectangle :\n";
			ar = l * b ;
			cout<< ar <<endl;
		}	
};
//multi level inheritance
class triangle
{
	public:
		int h,s1,s2;
		void read1()
		{
			cout<<"Enter height of triangle :\n";
			cin>>h;
			cout<<"Enter side 1 of triangle :\n";
			cin>>s1;
			cout<<"Enter side 2 of triangle :\n";
			cin>>s2;
		}
};
class perimeter: public triangle
{
	public:
		int peri;
		void perime()
		{
			cout<<"Perimeter of triangle :\n";
			peri = h + s1 + s2;
			cout<< peri <<endl;
		}		
};
class semiperimeter: public perimeter
{
	public:
		float semiperi;
		void semiperime()
		{
			cout<<"Semiperimeter of triangle :\n";
			semiperi = peri/2;
			cout<< semiperi <<endl;
		}
};
//multiple inheritance
class areacircle
{
	public:
		float pi=3.14,ar1;
		int rad;
		void area1()
		{
			cout<<"Enter radius of circle for area:\n";
			cin>>rad;
			ar1 = pi * rad * rad;
		}
};
class pericircle
{
	public:
		float pi=3.14,peric;
		int rad;
		void perimet()
		{
			cout<<"Enter radius of circle for perimeter:";
			cin>>rad;
			peric=2*pi*rad;
		}
};
class disparea:public pericircle,public areacircle
{
	public:
		void disp()
		{
			cout<<"Area of circle is :";
			cout<<ar1 <<endl;
			cout<<"Perimeter of circle :";
			cout<<peric <<endl;
		}
};

int main()
{
	int ch;
	rectangle ro;
	semiperimeter so;
	disparea d1;
	do 
	{
		cout << "\n***********Menu************";
		cout << "\n1. Single level inheritance :";
		cout << "\n2. Multi level inheritance :";
		cout << "\n3. Multiple inheritance :";
		cout << "\n4. Exit";
		cout << "\nEnter your choice: ";
		cin >> ch;

		switch (ch) 
		{
		    case 1:
		        cout << "\n1. Single level inheritance :\n";
		        ro.read();
		        ro.area();
		        break;
		    case 2:
		      	cout << "\n2. Multi level inheritance :\n";
		      	so.read1();
		      	so.perime();
		        break;
		    case 3:
		      	cout << "\n3. Multiple inheritance :\n";
		      	d1.area1();
		      	d1.perimet();
		      	d1.disp();
		        break;
		    case 4:
		        cout << "Exit\n";
		        break;
		}
    } while (ch != 4);
    return 0;
}
""")
def vector():
    print("""
#include <iostream>
using namespace std;
template <class T>
class vector {
    T v[20];
    int size;

public:
    void create();
    void modify();
    void mult();
    void display();
};
template <class T>
void vector<T>::create() {
    int i = 0;
    T value;
    char ans;
    size = 0;
    do {
        cout << "\nEnter the value :";
        cin >> value;
        v[i] = value;
        size++;
        i++;
        cout << "\nDo you want more elements (y/n)?";
        cin >> ans;
    } while (ans == 'y' || ans == 'Y');
}
template <class T>
void vector<T>::modify() {
    int key;
    T newval;
    cout << "\nEnter index to modification (0 to " << size - 1 << "): ";
    cin >> key;
    if (key >= 0 && key < size) { 
        cout << "\nEnter new value :";
        cin >> newval;
        v[key] = newval;
    } else {
        cout << "Invalid index!" << endl;
    }
}
template <class T>
void vector<T>::mult() {
    int i;
    int scalarval;
    cout << "\nEnter scalar value for multiplication :"; 
    cin >> scalarval;
    for (i = 0; i < size; i++) {
        v[i] = v[i] * scalarval;
    }
}
template <class T>
void vector<T>::display() {
    int i;
    cout << "\nSize of vector is :" << size;
    cout << "\nElements in vector are :";
    cout << "(";
    for (i = 0; i < size; i++) {
        cout << v[i];
        if (i < size - 1) {
            cout << ", "; 
        }
    }
    cout << ")";
    cout << endl; 
}
int main() {
    int ch;
    vector<int> obj;
    cout << "\nProgram for template class :";
    do {
        cout << "\nVector Operations Menu:\n";
        cout << "1. Create Vector\n";
        cout << "2. Modify Element\n";
        cout << "3. Multiply by Scalar\n";
        cout << "4. Display Vector\n";
        cout << "5. Exit\n";
        cout << "Enter your choice: ";
        cin >> ch;
        switch (ch) {
        case 1:
            obj.create();
            break;
        case 2:
            obj.modify();
            break;
        case 3:
            obj.mult();
            break;
        case 4:
            obj.display();
            break;
        case 5:
            cout << "Exiting program.\n";
            break;
        default:
            cout << "Invalid choice. Please try again.\n";
        }
    } while (ch != 5);
    return 0;
}
""")
def string():
    print("""
#include<iostream>
using namespace std;

class My_string
{
	public:
		char str[10], str1[10];
		int n=5,i;
		void create()
		{
			cout << "Enter elements of the first string:\n";
		    	for (int i = 0; i < n; i++) 
			{
				cin >> str[i];
			}
			cout << "Enter elements of the secong string:\n";
		    	for (int i = 0; i < n; i++) 
			{
				cin >> str1[i];
			}
		}
		void display()
		{
			cout << "Elements of the first string:\n";
			for (int i = 0; i < n; i++) 
			{
				cout << str[i] << " ";
				
			}
			cout << "\nElements of the second string:\n";
			for (int i = 0; i < n; i++) 
			{
				cout << str1[i] << " ";
				
			}
			cout << endl;
		}
		void concat()
		{
			for (int i = 0; i < n; i++) 
			{
				cout << str[i] << " ";
			}
			for (int i = 0; i < n; i++) 
			{
				cout << str1[i] << " ";
			}			
		}
		void length()
		{
			cout << "Length of string\n";
			cout << n ;
		}
		void reverse()
		{
			cout << "Elements of the string:\n";
			for (int i = n-1; i >= 0; i--) 
			{
				cout << str[i] << " ";
			}
			cout << endl;
		}
};

int main()
{
	My_string st;
	int ch;
	
	do 
	{
		cout << "\n*********Menu*********";
		cout << "\n1. Create String:";
		cout << "\n2. Display String:";
		cout << "\n3. Concatinate String:";
		cout << "\n4. Length of String:";
		cout << "\n5. Reverse String :";
		cout << "\n6. Exit";
		cout << "\nEnter your choice: ";
		cin >> ch;

		switch (ch) 
		{
		    case 1:
		        st.create();
		        break;
		    case 2:
		      	st.display();
		        break;
		    case 3:
		      	st.concat();
		        break;
		    case 4:
		      	st.length();
		        break;
		    case 5:
		      	st.reverse();
		        break;
		    case 6:
		        cout << "Exit\n";
		        break;
		}
    } while (ch != 6);

    return 0;
}
""")
def database1():
    print("""
#include <iostream>
#include <string>
#include <stdexcept>
using namespace std;
class Student {
private:
    string name;
    int rollNumber;
    string studentClass;
    char division;
    string dateOfBirth;
    string bloodGroup;
    string contactAddress;
    string telephoneNumber;
    string drivingLicenseNo;
public:
    Student(string n, int roll, string sClass, char div, string dob, string bg, string addr, string tel, string dl) 
        : name(n), rollNumber(roll), studentClass(sClass), division(div), 
          dateOfBirth(dob), bloodGroup(bg), contactAddress(addr), 
          telephoneNumber(tel), drivingLicenseNo(dl) 
    {
        cout << "Student record created for " << name << endl;
    }
    ~Student() {
        cout << "Student record for " << name << " is being deleted." << endl;
    }
    friend void displayStudent(const Student &s);
    void updateContactInfo(string newAddress, string newTel) {
        contactAddress = newAddress;
        telephoneNumber = newTel;
    }
    void validateRollNumber() {
        if (rollNumber <= 0) {
            throw invalid_argument("Roll number must be positive!");
        }
    }
    bool isSameClass(const Student &other) const {
        return this->studentClass == other.studentClass;
    }
};
void displayStudent(const Student &s) {
    cout << "\nStudent Information:\n";
    cout << "Name: " << s.name << "\nRoll Number: " << s.rollNumber 
         << "\nClass: " << s.studentClass << "\nDivision: " << s.division 
         << "\nDate of Birth: " << s.dateOfBirth << "\nBlood Group: " << s.bloodGroup 
         << "\nContact Address: " << s.contactAddress 
         << "\nTelephone Number: " << s.telephoneNumber 
         << "\nDriving License No: " << s.drivingLicenseNo << endl;
}
int main() {
    try {
        Student student1("John Doe", 101, "10th", 'A', "01/01/2005", "O+", "123 Main St", "123-456-7890", "DL12345");
        displayStudent(student1);
        student1.updateContactInfo("456 Elm St", "987-654-3210");
        cout << "\nAfter updating contact info:\n";
        displayStudent(student1);
        student1.validateRollNumber();
        Student student2("Jane Smith", 102, "10th", 'B', "15/02/2005", "A+", "789 Pine St", "321-654-0987", "DL67890");
        if (student1.isSameClass(student2)) {
            cout << "\nBoth students are in the same class." << endl;
        } else {
            cout << "\nThe students are in different classes." << endl;
        }
    } catch (const exception &e) {
        cerr << "Error: " << e.what() << endl;
    }
    return 0;
}    
    """)
def database2():
    print("""
#include <iostream>
#include <string>
#include <stdexcept>
using namespace std;
class Student {
private:
    string name;
    int rollNumber;
    string studentClass;
    char division;
    string dateOfBirth;
    string bloodGroup;
    string contactAddress;
    string telephoneNumber;
    string drivingLicenseNo;
public:
    Student() {
        cout << "\nEnter Student Details:\n";
        cout << "Name: ";
        getline(cin, name);
        cout << "Roll Number: ";
        cin >> rollNumber;
        cin.ignore();  // To ignore the newline character after rollNumber input
        cout << "Class: ";
        getline(cin, studentClass);
        cout << "Division (A/B/C...): ";
        cin >> division;
        cin.ignore();
        cout << "Date of Birth (DD/MM/YYYY): ";
        getline(cin, dateOfBirth);
        cout << "Blood Group: ";
        getline(cin, bloodGroup);
        cout << "Contact Address: ";
        getline(cin, contactAddress);
        cout << "Telephone Number: ";
        getline(cin, telephoneNumber);
        cout << "Driving License No: ";
        getline(cin, drivingLicenseNo);
        cout << "\nStudent record created for " << name << endl;
    }
    ~Student() {
        cout << "Student record for " << name << " is being deleted." << endl;
    }
    friend void displayStudent(const Student &s);
    void updateContactInfo() {
        cout << "\nUpdate Contact Information:\n";
        cout << "New Contact Address: ";
        getline(cin, contactAddress);
        cout << "New Telephone Number: ";
        getline(cin, telephoneNumber);
    }
    void validateRollNumber() {
        if (rollNumber <= 0) {
            throw invalid_argument("Roll number must be positive!");
        }
    }
    bool isSameClass(const Student &other) const {
        return this->studentClass == other.studentClass;
    }
};
void displayStudent(const Student &s) {
    cout << "\nStudent Information:\n";
    cout << "Name: " << s.name << "\nRoll Number: " << s.rollNumber
         << "\nClass: " << s.studentClass << "\nDivision: " << s.division
         << "\nDate of Birth: " << s.dateOfBirth << "\nBlood Group: " << s.bloodGroup
         << "\nContact Address: " << s.contactAddress
         << "\nTelephone Number: " << s.telephoneNumber
         << "\nDriving License No: " << s.drivingLicenseNo << endl;
}
int main() {
    try {
        Student student1;
        displayStudent(student1);
        student1.updateContactInfo();
        cout << "\nAfter updating contact info:\n";
        displayStudent(student1);
        student1.validateRollNumber();
    } catch (const exception &e) {
        cerr << "Error: " << e.what() << endl;
    }
    return 0;
}    
    """)
def publication1():
    print("""
#include <iostream>
#include <string>
#include <stdexcept>
using namespace std;
class Publication {
protected:
    string title;
    float price;
public:
    Publication() : title(""), price(0.0) {}
    virtual void getData() {
        cout << "Enter title: ";
        getline(cin, title);
        cout << "Enter price: ";
        cin >> price;
        cin.ignore(); // Ignore newline character after price input
    }
    virtual void displayData() const {
        cout << "Title: " << title << "\nPrice: $" << price << endl;
    }
    virtual ~Publication() {}
};
class Book : public Publication {
private:
    int pageCount;
public:
    Book() : pageCount(0) {}
    void getData() override {
        try {
            Publication::getData();
            cout << "Enter page count: ";
            cin >> pageCount;
            cin.ignore();
            if (pageCount < 0) {
                throw invalid_argument("Page count cannot be negative.");
            }
        } catch (const exception &e) {
            cerr << "Error: " << e.what() << endl;
            resetData();
        }
    }
    void displayData() const override {
        Publication::displayData();
        cout << "Page Count: " << pageCount << endl;
    }
    void resetData() {
        title = "";
        price = 0.0;
        pageCount = 0;
    }
};
class Tape : public Publication {
private:
    float playTime;
public:
    Tape() : playTime(0.0) {}
    void getData() override {
        try {
            Publication::getData();
            cout << "Enter play time (in minutes): ";
            cin >> playTime;
            cin.ignore();
            if (playTime < 0) {
                throw invalid_argument("Play time cannot be negative.");
            }
        } catch (const exception &e) {
            cerr << "Error: " << e.what() << endl;
            resetData();
        }
    }
    void displayData() const override {
        Publication::displayData();
        cout << "Play Time: " << playTime << " minutes" << endl;
    }
    void resetData() {
        title = "";
        price = 0.0;
        playTime = 0.0;
    }
};
int main() {
    cout << "\n--- Book Entry ---" << endl;
    Book book;
    book.getData();
    cout << "\n--- Book Details ---" << endl;
    book.displayData();
    cout << "\n--- Tape Entry ---" << endl;
    Tape tape;
    tape.getData();
    cout << "\n--- Tape Details ---" << endl;
    tape.displayData();
    return 0;
}    
    """)

