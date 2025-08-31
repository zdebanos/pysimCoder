all: dependencies allfiles lib install
reduced: files lib install

LIB = libpyblk.a
GENERIC_INC = $(PYSUPSICTRL)/CodeGen/Common/include
TARGET_INC = ../include
INCLUDE =  -I$(GENERIC_INC) -I$(TARGET_INC)

COMMON_DIR = $(PYSUPSICTRL)/CodeGen/Common
EXT_LIBS = $(PYSUPSICTRL)/ExtLibs
SHV_COMPILED_INC_PATH = $(EXT_LIBS)/shv-libs4c-nuttx/_compiled/include
SHV_COMPILED_LIB_PATH = $(EXT_LIBS)/shv-libs4c-nuttx/_compiled/lib
SHV_REVISION = $(shell head -n1 "$(COMMON_DIR)/shv/shv-libs4c-revision.txt")

NUTTX_EXPORT = $(PWD)/../nuttx-export

ifndef NUTTX_EXPORT
$(warning Specify NUTTX_EXPORT)
$(warning make_rtw NUTTX_EXPORT=/path/to/nuttx-export)
$(error NUTTX_EXPORT not defined, cannot continue)
endif

include $(NUTTX_EXPORT)/scripts/Make.defs
include $(NUTTX_EXPORT)/.config

SRCALL = $(wildcard $(COMMON_DIR)/common_dev/*.c)
SRCALL += $(wildcard $(COMMON_DIR)/posix/*.c)
SRCALL += serialOut.c

# Add the pysimCoder SHV adaptation sources
ifeq ($(SHV),1)
SRCALL += $(wildcard $(COMMON_DIR)/shv/*.c)
endif

SHV_IN_NUTTX := $(shell grep -wc "CONFIG_NETUTILS_LIBSHVC" $(NUTTX_EXPORT)/include/nuttx/config.h)
UNPACKLIB_DIR := $(PYSUPSICTRL)/CodeGen/nuttx/devices/unpacklib

ifeq ($(CONFIG_ADC),y)
SRCALL += nuttx_ADC.c
endif

ifeq ($(CONFIG_DAC),y)
SRCALL += nuttx_DAC.c
endif

ifeq ($(CONFIG_PWM),y)
SRCALL += nuttx_PWM.c
endif

ifeq ($(CONFIG_DEV_GPIO),y)
SRCALL += nuttxDI.c \
nuttxDO.c
endif

ifeq ($(CONFIG_SENSORS_QENCODER),y)
SRCALL += nuttxENC.c
endif

ifeq ($(CONFIG_SPI),y)
ifeq ($(CONFIG_SPI_EXCHANGE),y)
SRCALL += heater.c
SRCALL += RLC.c
SRCALL += DCMOT.c
SRCALL += nuttx_p3m_spi.c
SRCALL += pm_mc1_spi.c
endif
endif

ifeq ($(CONFIG_SENSORS_DHTXX),y)
SRCALL += sensors/nuttxDHTXX.c
endif

ifeq ($(CONFIG_MICROROSLIB),y)
SRCALL += microros.c
endif

have_can =
ifeq ($(CONFIG_CAN),y)
	have_can = yes
endif
ifeq ($(CONFIG_NET_CAN),y)
	have_can = yes
endif

ifdef have_can
SRCALL += canopen.c
SRCALL += $(wildcard $(COMMON_DIR)/CAN_dev/*.c)
SRCALL += $(wildcard $(COMMON_DIR)/Faulhaber_dev/*.c)
SRCALL += $(wildcard $(COMMON_DIR)/Maxon_dev/*.c)
endif

OBJ = $(notdir $(SRCALL:.c=.o))

CWD = $(shell pwd)

NUTTX_INCLUDES = -isystem $(NUTTX_EXPORT)/include

SYSTEM_LIBS += --start-group $(LDLIBS) $(EXTRA_LIBS) --end-group
ELF_MODULE_LIBS = --start-group $(EXTRA_LIBS) --end-group

LDFLAGS += -L $(NUTTX_EXPORT)/libs

ifneq ($(shell $(CC) --target-help | grep -e '-mlong-calls\b'),)
TARGET_ARCH_LONG_CALLS = -mlong-calls
endif

TARGET_ARCH_FLAGS ?= $(ARCHCFLAGS) $(ARCHCPUFLAGS) \
	$(TARGET_ARCH_LONG_CALLS) -fno-common -DWITHOUT_MLOCK

DEFAULT_OPT_OPTS ?= $(ARCHOPTIMIZATION)

ifndef OPT_OPTS
OPT_OPTS = $(DEFAULT_OPT_OPTS)
endif

LD_SCRIPT = $(NUTTX_EXPORT)/scripts/$(LDNAME)

LDFLAGS += -T $(LD_SCRIPT)

LDFLAGS  += --entry=__start -nostartfiles -nodefaultlibs

ELF_FILE_LDSCRIPT ?= $(wildcard $(NUTTX_EXPORT)/scripts/gnu-elf.ld)

INCLUDES += $(NUTTX_INCLUDES)

CFLAGS += $(TARGET_ARCH_FLAGS) $(ARCHWARNINGS) $(OPT_OPTS) $(INCLUDES)

CXXFLAGS = $(TARGET_ARCH_FLAGS) $(ARCHCXXFLAGS) $(ARCHWARNINGSXX) $(OPT_OPTS) $(INCLUDES)

OBJEX = $(SRC:.c=.o)
DEFINES = -D PLOTTER_SCRIPT=\"$(CWD)/scope.py\"
CC_FLAGS = -c $(DBG) $(INCLUDE) $(CFLAGS)
# Include the SHV include directories. Expect the headers at this exact location.
ifeq ($(SHV),1)
ifeq ($(SHV_IN_NUTTX),0)
CC_FLAGS += -I$(SHV_COMPILED_INC_PATH)
endif
CC_FLAGS += -I$(COMMON_DIR)/shv/include
endif
CC_FLAGS_SCP = -c $(DBG) $(INCLUDE) $(CFLAGS) $(DEFINES)
CC_FLAGS_FMU = -c $(DBG) $(INCLUDE) $(CFLAGS) -Wall -DFMI_COSIMULATION \
                             -DSTANDALONE_XML_PARSER -DLIBXML_STATIC \
                              -I$(FMUDIR)/fmuinc/include -I$(FMUDIR)/fmuinc/parser -I$(FMUDIR)/fmuinc

# Decide what SHV version we pick. In case the NuttX export has no SHV support,
# we clone the SHV as an external library and pack it inside $(LIB).
dependencies:
ifeq ($(SHV),1)
	@if [ "$(SHV_IN_NUTTX)" -lt 1 ]; then \
		echo "Silicon Heaven library was not found in NuttX, using a cloned one."; \
		cd $(EXT_LIBS); \
		if [ ! -e shv-libs4c-nuttx ]; then \
			if ! git clone https://github.com/silicon-heaven/shv-libs4c shv-libs4c-nuttx > /dev/null 2>&1; then \
				echo "Failed cloning the Silicon Heaven library, try again."; \
			else \
				( cd shv-libs4c-nuttx && \
				  git checkout $(SHV_REVISION) && \
				  git submodule update --recursive --init ) > /dev/null 2>&1; \
				make -C shv-libs4c-nuttx CONFIG_SHV_LIBS4C_PLATFORM="nuttx" \
					CC="$(CC)" \
					CXX="$(CXX)" \
					CFLAGS="$(CFLAGS)" \
					CXXFLAGS="$(CXXFLAGS)" \
					LD="$(LD)" \
					LDFLAGS="$(LDFLAGS)" \
					CONFIG_OC_ULUT_TESTS=n; \
			fi \
		fi \
	else \
		echo "Using the Silicon Heaven library from the NuttX build."; \
	fi
endif
	@cd $(PYSUPSICTRL)/CodeGen/nuttx/devices

allfiles:

files:
EXCLUDE = comedi_analog_input.c comedi_analog_output.c comedi_digital_input.c comedi_digital_output.c
SRC=$(filter-out $(EXCLUDE),$(SRCALL))

scope.o: scope.c
	$(CC) $(CC_FLAGS_SCP) $<

FMUinterface.o: FMUinterface.c
	$(CC) $(CC_FLAGS_FMU) $<

%.o: %.c
	@echo "CC: $$(basename $<)"
	@$(CC) $(CC_FLAGS) $<

%.o: sensors/%.c
	@echo "CC: sensors/$$(basename $<)"
	@$(CC) $(CC_FLAGS) $<

ifeq ($(SHV),1)
%.o: $(COMMON_DIR)/shv/%.c
	@echo "CC: shv/$$(basename $<)"
	@$(CC) $(CC_FLAGS) $<
endif

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

lib: $(OBJ)
ifeq ($(SHV),1)
	@ if [ "$(SHV_IN_NUTTX)" -lt 1 ]; then \
		echo "AR: *.o"; \
		echo "AR: libshvchainpack.a libshvtree.a libulut.a"; \
		mkdir -p $(UNPACKLIB_DIR); \
		cp $^ $(UNPACKLIB_DIR); \
		cd $(UNPACKLIB_DIR); \
		ar x $(SHV_COMPILED_LIB_PATH)/libshvchainpack.a; \
		ar x $(SHV_COMPILED_LIB_PATH)/libshvtree.a; \
		ar x $(SHV_COMPILED_LIB_PATH)/libulut.a; \
		$(AR) $(LIB) *.o; \
		cp $(LIB) ..; \
		rm -r $(UNPACKLIB_DIR); \
	else \
		echo "AR: *.o"; \
		$(AR) $(LIB) $(OBJ); \
	fi
else
	@echo "AR: *.o"
	@$(AR) $(LIB) $(OBJ)
endif

install:
	@mkdir -p ../lib
	@echo "MV: $(LIB) -> PYSUPSICTRL/CodeGen/nuttx/lib/$(LIB)"
	@mv $(LIB) $(PYSUPSICTRL)/CodeGen/nuttx/lib

clean:
	@echo "RM: shv-libs4c-nuttx"
	@echo "RM: $(LIB)"
	@echo "RM: *.o"
	@rm -rf $(EXT_LIBS)/shv-libs4c-nuttx
	@rm -f $(LIB) $(OBJ)
