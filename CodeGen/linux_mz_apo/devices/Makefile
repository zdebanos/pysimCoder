all: dependencies lib install
reduced: dependencies lib install

LIB = libpyblk.a
GENERIC_INC = $(PYSUPSICTRL)/CodeGen/Common/include
TARGET_INC = ../include
INCLUDE = -I$(GENERIC_INC) -I$(TARGET_INC)
COMMON_DIR = $(PYSUPSICTRL)/CodeGen/Common
EXT_LIBS = $(PYSUPSICTRL)/ExtLibs
SHV_COMPILED_INC_PATH = $(EXT_LIBS)/shv-libs4c-linux/_compiled/include
SHV_COMPILED_LIB_PATH = $(EXT_LIBS)/shv-libs4c-linux/_compiled/lib
SHV_REVISION = $(shell head -n1 "$(COMMON_DIR)/shv/shv-libs4c-revision.txt")

.PHONY: all dependencies clean install

SRCALL = $(wildcard *.c)
SRCALL += $(wildcard $(COMMON_DIR)/CAN_dev/*.c)
SRCALL += $(wildcard $(COMMON_DIR)/common_dev/*.c)
SRCALL += $(wildcard $(COMMON_DIR)/Faulhaber_dev/*.c)
SRCALL += $(wildcard $(COMMON_DIR)/Maxon_dev/*.c)
SRCALL += $(wildcard $(COMMON_DIR)/posix/*.c)

ifeq ($(SHV),1)
SRCALL += $(wildcard $(COMMON_DIR)/shv/*.c)
endif

UNPACKLIB_DIR := $(PYSUPSICTRL)/CodeGen/linux_mz_apo/devices/unpacklib

CWD = $(shell pwd)

######DBG = -g -fPIC
DBG = -g

CC = arm-linux-gnueabihf-gcc
AR = arm-linux-gnueabihf-ar
OBJEX = $(SRC:.c=.o)
INCLUDE =  -I$(GENERIC_INC) -I$(TARGET_INC)
CC_FLAGS = -c $(DBG) $(INCLUDE)
ifeq ($(SHV),1)
CC_FLAGS += -I$(COMMON_DIR)/shv/include
CC_FLAGS += -I$(SHV_COMPILED_INC_PATH)
endif
CC_FLAGS += -D CG_WITH_ENV_HOST_ADDR

dependencies:
ifeq ($(SHV),1)
	@ cd $(EXT_LIBS); \
	if [ ! -e shv-libs4c-linux ]; then \
		echo "Cloning shv-libs4c"; \
		if ! git clone https://github.com/silicon-heaven/shv-libs4c shv-libs4c-linux-mzapo > /dev/null 2>&1; then \
			echo "Failed cloning the Silicon Heaven library, try again."; \
		else \
			( cd shv-libs4c-linux-mzapo && \
			  git checkout $(SHV_REVISION) && \
			  git submodule update --recursive --init ) > /dev/null 2>&1; \
			make -C shv-libs4c-linux-mzapo CONFIG_SHV_LIBS4C_PLATFORM="linux" \
				CC="$(CC)" \
				CXX="$(CXX)" \
				CFLAGS="$(CFLAGS)" \
				CXXFLAGS="$(CXXFLAGS)" \
				LD="$(LD)" \
				LDFLAGS="$(LDFLAGS)" \
				CONFIG_OC_ULUT_TESTS=n; \
		fi \
	fi
endif

SRC=$(filter-out $(EXCLUDE),$(SRCALL))
OBJ = $(notdir $(SRCALL:.c=.o))

%.o: %.c
	@echo "CC: $$(basename $<)"
	@$(CC) $(CC_FLAGS) $<

%.o: $(COMMON_DIR)/CAN_dev/%.c
	@echo "CC: CAN_dev/$$(basename $<)"
	@$(CC) $(CC_FLAGS) $<

%.o: $(COMMON_DIR)/common_dev/%.c
	@echo "CC: common_dev/$$(basename $<)"
	@$(CC) $(CC_FLAGS) $<

%.o: $(COMMON_DIR)/Faulhaber_dev/%.c
	@echo "CC: Faulhaber_dev/$$(basename $<)"
	@$(CC) $(CC_FLAGS) $<

%.o: $(COMMON_DIR)/Maxon_dev/%.c
	@echo "CC: Maxon_dev/$$(basename $<)"
	@$(CC) $(CC_FLAGS) $<

%.o: $(COMMON_DIR)/posix/%.c
	@echo "CC: posix/$$(basename $<)"
	@$(CC) $(CC_FLAGS) $<

ifeq ($(SHV),1)
%.o: $(COMMON_DIR)/shv/%.c
	@echo "CC: shv/$$(basename $<)"
	@$(CC) $(CC_FLAGS) $<
endif

lib: $(OBJ)
ifeq ($(SHV),1)
	@ echo "AR: *.o"; \
	echo "AR: libshvchainpack.a libshvtree.a libulut.a"; \
	mkdir -p $(UNPACKLIB_DIR); \
	cp $^ $(UNPACKLIB_DIR); \
	cd $(UNPACKLIB_DIR); \
	ar x $(SHV_COMPILED_LIB_PATH)/libshvchainpack.a; \
	ar x $(SHV_COMPILED_LIB_PATH)/libshvtree.a; \
	ar x $(SHV_COMPILED_LIB_PATH)/libulut.a; \
	$(AR) rcs $(LIB) *.o; \
	cp $(LIB) ..; \
	rm -r $(UNPACKLIB_DIR)
else
	@echo "AR: *.o"
	@$(AR) rcs $(LIB) $(OBJ)
endif

install:
	@echo "MV: $(LIB) -> PYSUPSICTRL/CodeGen/linux_mz_apo/lib/$(LIB)"
	@mv $(LIB) ../lib

clean:
	@echo "RM: shv-libs4c-linux-mzapo"
	@echo "RM: $(LIB)"
	@echo "RM: *.o"
	@rm -rf $(EXT_LIBS)/shv-libs4c-linux-mzapo
	@rm -f $(LIB) $(OBJ)
