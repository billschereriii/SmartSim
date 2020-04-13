#include "client.h"
#include <mpi.h>

void test_3d_put_cpp(int dim1, int dim2, int dim3, std::string key_suffix="")
{
  SmartSimClient client;
  int rank;
  int n_ranks;
  int dims[3];
  std::string key;
  
  double ***arr = (double ***)malloc(dim1 * sizeof(double **));
  for (int i=0; i<dim1; i++) {
    arr[i] = (double **)malloc(dim2 * sizeof(double*));
    for(int j=0; j<dim2; j++){
      arr[i][j] = (double *)malloc(dim3 * sizeof(double));
    }  
  }

  int c = 0;
  for(int i = 0; i < dim1; i++)
    for(int j = 0; j < dim2; j++)
      for(int k = 0; k < dim3; k++)
	  arr[i][j][k] = c++;

  dims[0] = dim1;
  dims[1] = dim2;
  dims[2] = dim3;

  MPI_Comm_rank(MPI_COMM_WORLD, &rank);
  MPI_Comm_size(MPI_COMM_WORLD, &n_ranks);
  
  key = "3d_test_with_rank_"+std::to_string(rank)+"_"+key_suffix;

  double startPutTime = MPI_Wtime();
  client.put_array_double(key.c_str(), arr, dims, 3);
  double endPutTime = MPI_Wtime();

  MPI_Barrier(MPI_COMM_WORLD);
  
  if(!client.exists(key.c_str()))
    throw std::runtime_error("Key existence could not be verified with key_exists()");

  MPI_Barrier(MPI_COMM_WORLD);
  double globalSumPutTime = 0;
  double putTime = endPutTime - startPutTime;
  double minPutTime;
  double maxPutTime;
  MPI_Reduce(&putTime, &globalSumPutTime, 1, MPI_DOUBLE, MPI_SUM, 0,
             MPI_COMM_WORLD);
  MPI_Reduce(&putTime, &minPutTime, 1, MPI_DOUBLE, MPI_MIN, 0,
             MPI_COMM_WORLD);
  MPI_Reduce(&putTime, &maxPutTime, 1, MPI_DOUBLE, MPI_MAX, 0,
             MPI_COMM_WORLD);
  MPI_Barrier(MPI_COMM_WORLD);
  if(rank==0) {
    std::cout<<"Average put time "<<globalSumPutTime/n_ranks<<std::endl;
    std::cout<<"Min put time "<<minPutTime<<std::endl;
    std::cout<<"Max put time "<<maxPutTime<<std::endl;
  }
  
  double ***result = (double ***)malloc(dim1 * sizeof(double **));
  for (int i=0; i<dim1; i++) {
    result[i] = (double **)malloc(dim2 * sizeof(double*));
    for(int j=0; j<dim2; j++){
      result[i][j] = (double *)malloc(dim3 * sizeof(double));
    }
  }

  double startGetTime = MPI_Wtime();
  client.get_array_double(key.c_str(), result, dims, 3);
  double endGetTime = MPI_Wtime();

  MPI_Barrier(MPI_COMM_WORLD);
  double globalSumGetTime = 0;
  double getTime = endGetTime - startGetTime;
  double minGetTime;
  double maxGetTime;
  MPI_Reduce(&getTime, &globalSumGetTime, 1, MPI_DOUBLE, MPI_SUM, 0,
             MPI_COMM_WORLD);
  MPI_Reduce(&getTime, &minGetTime, 1, MPI_DOUBLE, MPI_MIN, 0,
             MPI_COMM_WORLD);
  MPI_Reduce(&getTime, &maxGetTime, 1, MPI_DOUBLE, MPI_MAX, 0,
             MPI_COMM_WORLD);
  MPI_Barrier(MPI_COMM_WORLD);
  if(rank==0) {
    std::cout<<"Average get time "<<globalSumGetTime/n_ranks<<std::endl;
    std::cout<<"Min get time "<<minGetTime<<std::endl;
    std::cout<<"Max get time "<<maxGetTime<<std::endl;
    std::cout<<"Data sent and received per rank (bytes): "<<sizeof(double)*dim1*dim2*dim3<<std::endl;
    std::cout<<"Total data sent and received (bytes): "<<sizeof(double)*dim1*dim2*dim3*n_ranks<<std::endl;
    std::cout<<"Total data sent and received (GB): "<<sizeof(double)*dim1*dim2*dim3*n_ranks/1.0E9<<std::endl;
  }
  
  for(int i = 0; i < dim1; i++)
    for(int j = 0; j < dim2; j++)
      for(int k = 0; k < dim3; k++) {
	if(!(result[i][j][k] == arr[i][j][k])) {
	  std::cout<<"result["<<i<<"]["<<j<<"]["<<k<<"] = "<<result[i][j][k]<<std::endl;
	  std::cout<<"arr["<<i<<"]["<<j<<"]["<<k<<"] = "<<arr[i][j][k]<<std::endl;
	  throw std::runtime_error("3D arrays using n_d array functiionality do not match");
	}
      }
  
  for(int i=0; i<dim1; i++) {
    for(int j=0; j<dim2; j++) {
      delete[] arr[i][j];
      delete[] result[i][j];
    }
    delete[] arr[i];
    delete[] result[i];
  }
  delete[] arr;
  delete[] result;
  
  if(rank == 0)
    std::cout<<"Finished 3d put/get c++ test"<<std::endl;

  return;
}

int main(int argc, char* argv[]) {

  MPI_Init(&argc, &argv);

  int rank;
  MPI_Comm_rank(MPI_COMM_WORLD, &rank);
  
  test_3d_put_cpp(atoi(argv[1]), atoi(argv[1]), atoi(argv[1]));
  MPI_Finalize();
  
  return 0;
}
