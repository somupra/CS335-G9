
int main(){
	int i ; 
	int arr[100][200];
	int b = 6;
	int c = 4;
	int d ;
	for(i=0 ; i<100 ; i++){
		b = arr[i] * arr[i+1] ;
		c = arr[i] / arr[i+1] ;
		d = b + c ;
	}	
	return 0 ;
}
