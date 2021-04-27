int main()
{
	int a ;
	int b ;
	int i ;
	a = 7 ;
	b = 5 ;
	if(a>b){
		int x ;
		x = 7.2 ;
	}
	else{
		int y ;
		y = 99 ;
	}
	b = 11 ;
	
	while(a>b){
		a = a+1 ;
		b = b-1 ;
	}
	a = b ;
	
	for(a=0 ; a<5 ; a=2*a ){
		b = b-a ;
	}
	b = a-1 ;
}
