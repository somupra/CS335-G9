
int main(){
	int a, b, c, d, e ;
	d = 5;
	e = 5;
	a = 7 ;
	b = a ;
	while(a<10){
		b = a+1 ;
		a++ ;
		c = b*a ;
		d = b/a ;
		e = c%d ;
		printf("%d, %d, %d\n", c, d, e) ;
	}
	
	if(a>b || c<d){
		printf("hello, %d, %d, %d, %d", a, b, c, d) ;
	}
	else{
		printf("%d, %d, %d, %d", a, b, c, d) ;		
	}
	return 0 ;
}
