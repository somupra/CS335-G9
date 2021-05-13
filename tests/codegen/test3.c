
int main(){
	int a, b, c, d, e ;
	d = 5;
	e = 5;
	a = 7 ;
	b = a ;
	for(c=0 ; c<10 ; c++){
		b++ ;
		a = b-c ;
		if(b==c/2){
			break ;
		}
		else{
			continue ;
		}
	}
	printf("%d, %d, %d, %d", a, b, c, d) ;
	return 0 ;
}
