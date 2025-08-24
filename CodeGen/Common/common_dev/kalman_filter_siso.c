/*
  COPYRIGHT (C) 2025 Stepan Pressl 
    <pressl.stepan@gmail.com>
    <pressste@fel.cvut.cz>

  This library is free software; you can redistribute it and/or
  modify it under the terms of the GNU Lesser General Public
  License as published by the Free Software Foundation; either
  version 2 of the License, or (at your option) any later version.

  This library is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
  Lesser General Public License for more details.

  You should have received a copy of the GNU Lesser General Public
  License along with this library; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA.
*/

#include <pyblock.h>
#include <matop.h>

static void init(python_block *block)
{
  double *realPar = block->realPar;
  int *intPar     = block->intPar;

  /* zero out the states */
  
  int nx = intPar[0];
  int ix_hatk = intPar[7];
  int ix_bark = intPar[8];
  double *x_hatk = &realPar[ix_hatk];
  double *x_bark = &realPar[ix_bark];
  
  for (int i = 0; i < nx; ++i) {
    x_hatk[i] = 0;
    x_bark[i] = 0;
  }
}

static void end(python_block *block)
{
  /* No operation */ 
}

static void inout(python_block *block) {
  /* the Prediction step: x_hat <- A x_bar[k-1] + B u[k-1] */
  /* x_hat is the output of the prediction */
  
  double *realPar = block->realPar;
  int *intPar     = block->intPar;
  double *u       = block->u[1]; /* It's actually the second input */
  double **y      = (double **) block->y;

  /* The data indexes */

  int nx = intPar[0];
  int nu = intPar[1];
  int iA = intPar[3];
  int iB = intPar[4];
  int ix_hatk = intPar[7];
  int ix_bark = intPar[8];
  double temp[nx], temp2[nx];

  double *A = &realPar[iA];
  double *B = &realPar[iB];
  double *x_hatk = &realPar[ix_hatk];
  double *x_bark = &realPar[ix_bark];

  matmult(B, nx, 1, u, 1, 1, temp);
  matmult(A, nx, nx, x_bark, nx, 1, temp2);
  matsum(temp, nx, 1, temp2, nx, 1, x_hatk);
  
  /* Output the estimation */

  for (int i = 0; i < nx; ++i) {
    y[i][0] = x_hatk[i];
  }
}

static void update(python_block *block)
{
  /* the Data step x_bar[k] <- x_hat[k] + K (y[k] - C x_hat[k]) */
  /* x_bar[k] is the prediction before the input */
  
  double *realPar = block->realPar;
  int *intPar     = block->intPar;

  /* The data indexes */

  int nx = intPar[0];
  int ny = intPar[2];
  int iC = intPar[5];
  int iK = intPar[6];
  int ix_hatk = intPar[7];
  int ix_bark = intPar[8];
  
  double *C = &realPar[iC];
  double *K = &realPar[iK];
  double *x_hatk = &realPar[ix_hatk];
  double *x_bark = &realPar[ix_bark];
  double temp;

  /* y[k] is actually the input */

  double *y = (double *) block->u[0];

  matmult(C, 1, nx, x_hatk, nx, 1, &temp);
  temp = y[0] - temp;
  matmult(K, nx, 1, &temp, 1, 1, x_bark);
  *x_bark += *x_hatk;
}

void kalman_filter_siso(int flag, python_block *block)
{
  if (flag == CG_OUT) {          /* Get input */
    inout(block);
  } else if (flag == CG_STUPD) { /* State update */
    update(block);
  } else if (flag==CG_END) {     /* Termination */ 
    end(block);
  } else if (flag == CG_INIT) {  /* Initialisation */
    init(block);
  }
}
