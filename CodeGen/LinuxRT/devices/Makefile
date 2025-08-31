all: dependencies files allfiles lib install
reduced: files lib install

LIB = libpyblk.a
GENERIC_INC = $(PYSUPSICTRL)/CodeGen/Common/include
TARGET_INC = ../include
INCLUDE = -I$(GENERIC_INC) -I$(TARGET_INC)
COMMON_DIR = $(PYSUPSICTRL)/CodeGen/Common
EXT_LIBS = $(PYSUPSICTRL)/ExtLibs
SHV_COMPILED_INC_PATH = $(EXT_LIBS)/shv-libs4c-linux/_compiled/include
SHV_COMPILED_LIB_PATH = $(EXT_LIBS)/shv-libs4c-linux/_compiled/lib
SHV_REVISION = $(shell head -n1 "$(COMMON_DIR)/shv/shv-libs4c-revision.txt")

.PHONY: all dependencies clean install allfiles

SRCALL = $(wildcard *.c)
SRCALL += $(wildcard $(COMMON_DIR)/CAN_dev/*.c)
SRCALL += $(wildcard $(COMMON_DIR)/common_dev/*.c)
SRCALL += $(wildcard $(COMMON_DIR)/Faulhaber_dev/*.c)
SRCALL += $(wildcard $(COMMON_DIR)/Maxon_dev/*.c)
SRCALL += $(wildcard $(COMMON_DIR)/posix/*.c)
SRCALL += $(wildcard $(COMMON_DIR)/AR2INO/*.c)

ifeq ($(SHV),1)
SRCALL += $(wildcard $(COMMON_DIR)/shv/*.c)
endif

UNPACKLIB_DIR := $(PYSUPSICTRL)/CodeGen/LinuxRT/devices/unpacklib

OBJ = $(notdir $(SRCALL:%.c=%.o))

CWD = $(shell pwd)
FMUDIR = ../fmu

######DBG = -g -fPIC
DBG = -g

CC ?= cc
AR ?= ar
OBJEX = $(SRC:.c=.o)
DEFINES_SCP = -D PLOTTER_SCRIPT=\"$(CWD)/scope.py\"
DEFINES_LED = -D LED_SCRIPT=\"$(CWD)/led.py\"
CC_FLAGS = -c $(DBG) $(INCLUDE)
ifeq ($(SHV),1)
CC_FLAGS += -I$(COMMON_DIR)/shv/include
CC_FLAGS += -I$(SHV_COMPILED_INC_PATH)
endif
CC_FLAGS += -D CG_WITH_ENV_HOST_ADDR
CC_FLAGS_SCP = -c $(DBG) $(INCLUDE)  $(DEFINES_SCP)
CC_FLAGS_LED = -c $(DBG) $(INCLUDE)  $(DEFINES_LED)
CC_FLAGS_FMU = -c $(DBG) $(INCLUDE) -Wall -DFMI_COSIMULATION \
                             -DSTANDALONE_XML_PARSER -DLIBXML_STATIC \
                              -I$(FMUDIR)/fmuinc/include -I$(FMUDIR)/fmuinc/parser -I$(FMUDIR)/fmuinc

dependencies:
ifeq ($(SHV),1)
	@ cd $(EXT_LIBS); \
	if [ ! -e shv-libs4c-linux ]; then \
		echo "Cloning shv-libs4c"; \
		if ! git clone https://github.com/silicon-heaven/shv-libs4c shv-libs4c-linux > /dev/null 2>&1; then \
			echo "Failed cloning the Silicon Heaven library, try again."; \
		else \
			( cd shv-libs4c-linux && \
			  git checkout $(SHV_REVISION) && \
			  git submodule update --recursive --init ) > /dev/null 2>&1; \
			make -C shv-libs4c-linux CONFIG_SHV_LIBS4C_PLATFORM="linux" \
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
	@cd $(PYSUPSICTRL)/CodeGen/LinuxRT/devices

allfiles:

files:
EXCLUDE = comedi_analog_input.c comedi_analog_output.c comedi_digital_input.c comedi_digital_output.c
SRC=$(filter-out $(EXCLUDE),$(SRCALL))

scope.o: scope.c
	@echo "CC: $<"
	@$(CC) $(CC_FLAGS_SCP) $<

led.o: led.c
	@echo "CC: $<"
	@$(CC) $(CC_FLAGS_LED) $<

FMUinterface.o: FMUinterface.c
	@echo "$CC: $<"
	@$(CC) $(CC_FLAGS_FMU) $<

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

%.o: $(COMMON_DIR)/AR2INO/%.c
	@echo "CC: AR2INO/$$(basename $<)"
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
	@echo "MV: $(LIB) -> PYSUPSICTRL/CodeGen/LinuxRT/lib/$(LIB)"
	@mv $(LIB) ../lib

clean:
	@echo "RM: shv-libs4c-linux"
	@echo "RM: $(LIB)"
	@echo "RM: *.o"
	@rm -rf $(EXT_LIBS)/shv-libs4c-linux
	@rm -f $(LIB) $(OBJ)
